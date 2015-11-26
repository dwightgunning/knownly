import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView, TemplateView
from dropbox.client import DropboxOAuth2Flow
from dropbox.rest import ErrorResponse

from knownly.console.services import DropboxUserService

logger = logging.getLogger(__name__)

User = get_user_model()

MESSAGE_SUCCESSFUL_AUTHORISATION = 'Knownly successfully authorised.'

MESSAGE_APP_NOT_APPROVED = 'Dropbox indicated that the request ' \
                           'for access was not approved. If this ' \
                           'was a mistake just hit the ' \
                           'button below to try again.'

MESSAGE_ACCOUNT_AUTH_ERROR = 'Account authentication error.'


def get_dropbox_auth_redirect(request):
    if request.is_secure() or not settings.DEBUG:
        protocol = 'https://'
    else:
        protocol = 'http://'

    return '%s%s%s' % (protocol,
                       request.META['HTTP_HOST'],
                       reverse('dropbox_auth_finish'))


class DropboxAuthStartView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        post_dropbox_auth_redirect = get_dropbox_auth_redirect(self.request)

        flow = DropboxOAuth2Flow(
            settings.DROPBOX_APP_KEY,
            settings.DROPBOX_APP_SECRET,
            post_dropbox_auth_redirect,
            self.request.session,
            'dropbox-auth-csrf-token')

        return flow.start()


class DropboxAuthCompleteView(RedirectView):

    def get_redirect_url(self, **kwargs):
        post_dropbox_auth_redirect = get_dropbox_auth_redirect(self.request)

        try:
            # Complete the Dropbox OAuth2 Flow
            flow = DropboxOAuth2Flow(
                settings.DROPBOX_APP_KEY,
                settings.DROPBOX_APP_SECRET,
                post_dropbox_auth_redirect,
                self.request.session,
                'dropbox-auth-csrf-token')

            dropbox_token, user_id, url_state = flow.finish(self.request.GET)
        except DropboxOAuth2Flow.NotApprovedException:
            logger.warn("Dropbox OAuth error: app not approved")
            messages.add_message(self.request,
                                 messages.WARNING,
                                 MESSAGE_APP_NOT_APPROVED)
        except ErrorResponse:
            # Present a useful error to the user
            logger.exception("Dropbox API error")
            messages.add_message(self.request,
                                 messages.ERROR,
                                 MESSAGE_ACCOUNT_AUTH_ERROR)
            logout(self.request)
        except Exception:
            logger.exception("Unexpected error occured during Dropbox auth")
            messages.add_message(self.request,
                                 messages.ERROR,
                                 MESSAGE_ACCOUNT_AUTH_ERROR)
            logout(self.request)
        else:
            # Create DropboxUser
            user_service = DropboxUserService()
            dropbox_user, created = user_service.get_or_create(user_id,
                                                               dropbox_token)

            # Login the dropbox user and setup session token
            dropbox_user.django_user.backend = \
                'django.contrib.auth.backends.ModelBackend'
            login(self.request, dropbox_user.django_user)

            if created:
                messages.add_message(self.request,
                                     messages.SUCCESS,
                                     MESSAGE_SUCCESSFUL_AUTHORISATION)
            else:
                return reverse('post_auth_existing_customer')

        return reverse('post_auth_new_customer')


class DropboxAuthSuccessView(TemplateView):
    template_name = "billing/auth_return.html"
    new_customer = False

    def get_context_data(self, **kwargs):
        context = super(DropboxAuthSuccessView, self) \
            .get_context_data(**kwargs)
        context['new_customer'] = self.new_customer
        return context
