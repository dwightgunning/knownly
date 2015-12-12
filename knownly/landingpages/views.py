import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView, TemplateView
from dropbox.oauth import (BadRequestException, BadStateException,
                           CsrfException, DropboxOAuth2Flow,
                           NotApprovedException, ProviderException)

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

        authorize_url = DropboxOAuth2Flow(
            settings.DROPBOX_APP_KEY,
            settings.DROPBOX_APP_SECRET,
            post_dropbox_auth_redirect,
            self.request.session,
            'dropbox-auth-csrf-token').start()

        return authorize_url


class DropboxAuthCompleteView(RedirectView):

    def get_redirect_url(self, **kwargs):
        post_dropbox_auth_redirect = get_dropbox_auth_redirect(self.request)

        try:
            # Complete the Dropbox OAuth2 Flow
            db_token, db_account_id, url_state = \
                DropboxOAuth2Flow(
                    settings.DROPBOX_APP_KEY,
                    settings.DROPBOX_APP_SECRET,
                    post_dropbox_auth_redirect,
                    self.request.session,
                    'dropbox-auth-csrf-token').finish(self.request.GET)
        except BadRequestException:
            logger.exception("Dropbox API error")
            messages.add_message(self.request,
                                 messages.ERROR,
                                 MESSAGE_ACCOUNT_AUTH_ERROR)
            logout(self.request)
        except BadStateException:
            logger.exception("Dropbox OAuth error")
            messages.add_message(self.request,
                                 messages.ERROR,
                                 MESSAGE_ACCOUNT_AUTH_ERROR)
            return reverse('post_auth_new_customer')
        except CsrfException:
            logger.exception("Dropbox OAuth error")
            messages.add_message(self.request,
                                 messages.ERROR,
                                 MESSAGE_ACCOUNT_AUTH_ERROR)
            return reverse('post_auth_new_customer')
        except NotApprovedException:
            logger.exception("Dropbox OAuth error")
            messages.add_message(self.request,
                                 messages.WARNING,
                                 MESSAGE_APP_NOT_APPROVED)
            return reverse('post_auth_new_customer')
        except ProviderException:
            logger.exception("Dropbox OAuth error")
            messages.add_message(self.request,
                                 messages.ERROR,
                                 MESSAGE_ACCOUNT_AUTH_ERROR)
            return reverse('post_auth_new_customer')

        dropbox_user, created = \
            DropboxUserService(db_token).get_or_create(db_account_id)

        # Login the dropbox user and setup session token
        dropbox_user.django_user.backend = \
            'django.contrib.auth.backends.ModelBackend'
        login(self.request, dropbox_user.django_user)

        if created:
            messages.add_message(self.request,
                                 messages.SUCCESS,
                                 MESSAGE_SUCCESSFUL_AUTHORISATION)
            return reverse('post_auth_new_customer')
        else:
            return reverse('post_auth_existing_customer')


class DropboxAuthSuccessView(TemplateView):
    template_name = "billing/auth_return.html"
    new_customer = False

    def get_context_data(self, **kwargs):
        context = super(DropboxAuthSuccessView, self) \
            .get_context_data(**kwargs)
        context['new_customer'] = self.new_customer
        return context
