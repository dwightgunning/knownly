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
from rest_framework import serializers as rest_serializers
from rest_framework import status
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.generics import (ListCreateAPIView, RetrieveDestroyAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from knownly.console import serializers
from knownly.console.exceptions import DropboxWebsiteError
from knownly.console.models import (ArchivedDropboxSite, DropboxSite,
                                    DropboxUser)
from knownly.console.services import DropboxSiteService, DropboxUserService
from knownly.console.tasks import process_dropbox_user_activity

logger = logging.getLogger(__name__)


class IndexView(TemplateView):

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            try:
                db_user = DropboxUser.objects.get(
                    django_user=self.request.user)
                DropboxUserService(db_user.dropbox_token).get_user(
                    db_user.user_id)
                return self._serve_app(self.request)
            except:
                message = 'Account authentication error.'
                messages.add_message(self.request, messages.ERROR, message)
                logger.exception('%s: %s' % (message, self.request.user))
                logout(self.request)

        return self._serve_public_index(self.request)

    def _serve_public_index(self, request, *args, **kwargs):
        self.template_name = 'landingpages/public.html'
        return super(IndexView, self).get(request, *args, **kwargs)

    def _serve_app(self, request, *args, **kwargs):
        if settings.DEBUG or hasattr(settings, 'TEST') and settings.TEST:
            logger.warning("Django serving the static angular index")
            return static.serve(request, 'index.html',
                                document_root=settings.STATIC_ROOT)
        else:
            response = HttpResponse(content_type='text/html; charset=utf-8')
            response['X-Accel-Redirect'] = '/ng-index.html'
            return response


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
                                 request.data, sha256).hexdigest():
            logger.error("Invalid HEX code provided.")
        else:
            logger.debug("Dropbox updates received...")
            for dropbox_token in \
                    json.loads(request.data)['list_folder']['accounts']:
                process_dropbox_user_activity.delay(dropbox_token)

        return HttpResponse(status=200)


class ProfileView(RetrieveUpdateAPIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
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
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, )
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

        # First persist the site model
        try:
            db_site_service = DropboxSiteService(dropbox_user)
            site = db_site_service.create(serializer.validated_data)
        except DropboxWebsiteError as dwe:
            logger.exception("Unable to create website")
            raise rest_serializers.ValidationError(
                {'error': [dwe.message]})

        # After the site model is stored, upload the template
        try:
            db_site_service.upload_template(site)
        except DropboxWebsiteError as dwe:
            logger.exception("Unable to upload")
            self.messages.append(dwe.message)
        except:
            # Catch and ignore so the user still receives a 201 Created
            logger.exception("Unable to upload")
            self.messages.append('There was an unexpected error while '
                                 'uploading your website folder to Dropbox. '
                                 'Please create it manually at /Apps/%s/%s'
                                 % (settings.DROPBOX_APP, site.domain))


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
            date_modified=dropbox_website.date_modified)

        dropbox_website.delete()
