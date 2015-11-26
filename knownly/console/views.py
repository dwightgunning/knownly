import hmac
import json
import logging
from hashlib import sha256

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import Http404, HttpResponse
from django.views import static
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse
from rest_framework import serializers as rest_serializers
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView, RetrieveDestroyAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from knownly.console import serializers
from knownly.console.exceptions import DropboxWebsiteError
from knownly.console.models import (ArchivedDropboxSite, DropboxSite,
                                    DropboxUser)
from knownly.console.services import DropboxSiteService
from knownly.console.tasks import process_dropbox_user_activity

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

        if self.dropbox_user:
            if settings.DEBUG or hasattr(settings, 'TEST') and settings.TEST:
                return static.serve(request,
                                    'index.html',
                                    document_root=settings.STATIC_ROOT)
            else:
                response = HttpResponse(
                    content_type='text/html; charset=utf-8')
                response['X-Accel-Redirect'] = '/index.html'
                return response
        else:
            self.template_name = 'landingpages/public.html'
            return super(IndexView, self).get(request, *args, **kwargs)


class LogoutDropboxUserView(TemplateView):
    template_name = 'logout.html'

    def dispatch(self, *args, **kwargs):
        logout(self.request)
        return super(LogoutDropboxUserView, self).dispatch(*args, **kwargs)


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.messages = []
        self._perform_create(serializer)

        response_data = {
            'dropbox_site': serializer.data
        }
        if self.messages:
            response_data['messages'] = self.messages

        headers = self.get_success_headers(response_data)
        return Response(response_data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def _perform_create(self, serializer):
        dropbox_user = DropboxUser.objects.get(django_user=self.request.user)

        try:
            db_site_service = DropboxSiteService(dropbox_user)
            site = db_site_service.create(serializer.validated_data)
        except Exception:
            logger.exception("Could not create the Dropbox Website")
            raise rest_serializers.ValidationError(
                {'error': ['An unexpected error occured. Please try again.']})

        try:
            db_site_service.upload_template(site)
        except DropboxWebsiteError as dwe:
            self.messages.append(dwe.message)


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
