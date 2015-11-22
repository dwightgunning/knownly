import hmac
import json
import logging
from hashlib import sha256

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.edit import BaseFormView, DeleteView
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse
from rest_framework.generics import (ListCreateAPIView, RetrieveDestroyAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated

from knownly.console import serializers
from knownly.console.exceptions import DropboxWebsiteError
from knownly.console.forms import WebsiteForm
from knownly.console.models import (ArchivedDropboxSite, DropboxSite,
                                    DropboxUser)
from knownly.console.services import DropboxWebsiteService
from knownly.console.tasks import process_dropbox_user_activity
from knownly.plans.models import CustomerSubscription

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    dropbox_user = None

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            self.dropbox_user = DropboxUser.objects.get(
                django_user=request.user)

            if self.dropbox_user.dropbox_token:
                client = DropboxClient(self.dropbox_user.dropbox_token)
                try:
                    client.account_info()
                except ErrorResponse as e:
                    logger.exception("Account authentication problem.")
                    # Remove the dead user_access token
                    self.dropbox_user.access_token = ''
                    self.dropbox_user.save()
                    self.dropbox_user = None

                    logout(self.request)
                    # Present a useful error to the user
                    message = 'Account authentication error.'
                    try:
                        message = '%s %s' % (messages, e.user_error_message)
                    except AttributeError as e:
                        logger.exception(e)
                        pass

                    messages.add_message(request, messages.ERROR, message)

        return super(IndexView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if self.dropbox_user:
            context['dropbox_user'] = self.dropbox_user
            context['websites'] = DropboxSite.objects.filter(
                dropbox_user=self.dropbox_user)
            context['create_website_form'] = WebsiteForm(
                {'dropboxy_user': self.dropbox_user})
            context['subscription'] = CustomerSubscription.objects.get(
                user=self.request.user)
            self.template_name = 'console/index.html'
        else:
            self.template_name = 'landingpages/public.html'

        return context


class LogoutDropboxUserView(TemplateView):
    template_name = 'logout.html'

    def dispatch(self, *args, **kwargs):
        logout(self.request)
        return super(LogoutDropboxUserView, self).dispatch(*args, **kwargs)


class CreateWebsiteView(BaseFormView):
    success_url = '/'
    form_class = WebsiteForm
    http_method_names = ['post', 'put', 'options', 'trace']

    def dispatch(self, request, *args, **kwargs):
        try:
            self.dropbox_user = \
                DropboxUser.objects.get(django_user=self.request.user)
        except DropboxUser.DoesNotExist:
            return HttpResponse('Unauthorized', status=401)

        if not request.is_ajax():
            return HttpResponseBadRequest("Only accepts XHR.")

        return super(CreateWebsiteView, self).dispatch(request,
                                                       *args,
                                                       **kwargs)

    def form_valid(self, form):
        try:
            website = DropboxWebsiteService.create_website(self.dropbox_user,
                                                           form.cleaned_data)

            message = 'A website folder ' \
                      '(<em>/Apps/Knownly.net/%s</em>)' \
                      ' has been created in your Dropbox.' % website.domain

        except DropboxWebsiteError as dwe:
            message = dwe.message
        except Exception:
            logger.exception("Could not create the Dropbox Website")
            message = "An unexpected error occured. Please try again"

        return self.render_to_json_response(
            {
                'domain': form.cleaned_data["domain"].domain,
                'message': message
            })

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors, status=400)

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)


class RemoveWebsiteView(DeleteView):
    success_url = '/'
    model = DropboxSite
    http_method_names = ['post', 'put', 'delete', 'options', 'trace']

    def dispatch(self, request, *args, **kwargs):
        try:
            self.dropbox_user = \
                DropboxUser.objects.get(django_user=self.request.user)
        except DropboxUser.DoesNotExist:
            return HttpResponse('Unauthorized', status=401)

        if not request.is_ajax():
            return HttpResponseBadRequest("Only accepts XHR.")

        return super(RemoveWebsiteView, self).dispatch(request,
                                                       *args,
                                                       **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            dropbox_website = DropboxSite.objects.get(
                domain__iexact=self.request.POST['domain'])
        except DropboxSite.DoesNotExist:
            logger.exception('Attempt to delete site that doesn\'t exist. '
                             'Domain: %s' % self.request.POST['domain'])
            context = {'message': 'Website not known at Knonwly.'}
            return self.render_to_json_response(context, status=400)

        if dropbox_website.dropbox_user != self.dropbox_user:
            logger.error('Attempt to delete site that doesn\'t belong to '
                         'user making request')
            context = {'message': 'Permission denied. Our team are '
                       'looking into this.'}
            return self.render_to_json_response(context, status=400)

        archived_site = \
            ArchivedDropboxSite(dropbox_user=dropbox_website.dropbox_user,
                                domain=dropbox_website.domain,
                                date_created=dropbox_website.date_created,
                                date_activated=dropbox_website.date_activated,
                                date_modified=dropbox_website.date_modified,
                                dropbox_hash=dropbox_website.dropbox_hash)

        archived_site.save()
        dropbox_website.delete()

        context = {'domain': dropbox_website.domain,
                   'message': 'Website %s removed.' % dropbox_website.domain}
        return self.render_to_json_response(context, status=200)

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)


@csrf_exempt
def dropbox_webhook(request):
    if request.method == 'GET':
        challenge = request.GET.get('challenge', '')
        return HttpResponse(status=200, content=challenge)
    elif request.method == 'POST':
        signature = request.META.get('HTTP_X_DROPBOX_SIGNATURE')
        if signature != hmac.new(settings.DROPBOX_APP_SECRET,
                                 request.body, sha256).hexdigest():
            logger.error("Invalid HEX code provided.")
            return HttpResponse(status=403)
        else:
            logger.debug("Dropbox updates received...")
            for uid in json.loads(request.body)['delta']['users']:
                if DropboxUser.objects.filter(user_id=uid).exists():
                    logger.debug('Dropbox webhook - updated user: %s', uid)
                    process_dropbox_user_activity.delay(uid)
                else:
                    logger.warn('Unrecognised dropbox user: %s', uid)

        return HttpResponse(status=200)


class ProfileView(RetrieveUpdateAPIView):
    authentication_classes = (IsAuthenticated,)
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            raise Http404

    def perform_update(self, serializer):
        super(ProfileView, self).perform_update(serializer)
        logger.warn('User profile updated: %s' % serializer.data)


class DropboxSiteListCreateView(ListCreateAPIView):
    serializer_class = serializers.DropboxSiteSerializer

    def get_queryset(self):
        dropbox_user = DropboxUser.objects.get(django_user=self.request.user)

        return DropboxSite.objects.filter(dropbox_user=dropbox_user)

    def perform_create(self, serializer):
        serializer.save(
            dropbox_user=DropboxUser.objects.get(
                django_user=self.request.user))


class DropboxSiteRetrieveDestroyView(RetrieveDestroyAPIView):
    serializer_class = serializers.DropboxSiteSerializer
    lookup_field = 'domain'

    def get_queryset(self):
        return DropboxSite.objects.filter(
            dropbox_user__django_user=self.request.user)

    def perform_destroy(self, dropbox_website):
        ArchivedDropboxSite.objects.create(
            dropbox_user=dropbox_website.dropbox_user,
            domain=dropbox_website.domain,
            date_created=dropbox_website.date_created,
            date_activated=dropbox_website.date_activated,
            date_modified=dropbox_website.date_modified,
            dropbox_hash=dropbox_website.dropbox_hash)

        dropbox_website.delete()
