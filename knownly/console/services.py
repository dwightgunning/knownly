import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from dropbox import Dropbox
from dropbox.exceptions import ApiError, DropboxException

from knownly.console.exceptions import (DropboxWebsiteError,
                                        KnownlyAuthAccountInactiveException,
                                        KnownlyAuthRegistrationsDisabled)
from knownly.console.models import DropboxSite, DropboxUser
from knownly.console.tasks import (fetch_website_folder_cursor,
                                   refresh_website_bearer_tokens_for_user)
from knownly.plans.services import QuotaService

logger = logging.getLogger(__name__)

User = get_user_model()


class DropboxUserService(object):

    def __init__(self, db_token, dropbox=None):
        self.db_token = db_token

        if dropbox:
            self.dropbox = dropbox
        else:
            self.dropbox = Dropbox(db_token)

    @transaction.atomic
    def get_user(self, db_user_id):

        try:
            db_user = DropboxUser.objects.get(
                user_id=db_user_id,
                defaults={'dropbox_token': self.db_token})
        except DropboxUser.DoesNotExist:
            raise KnownlyAuthRegistrationsDisabled

        if not db_user.django_user.is_active:
            raise KnownlyAuthAccountInactiveException

        db_user.dropbox_token = self.db_token
        db_user.save(update_fields=['dropbox_token'])
        try:
            refresh_website_bearer_tokens_for_user.delay(db_user.id)
        except:
            logger.exception("Could not clear bearer token for: %s"
                             % db_user.user_id)

        return db_user


class DropboxSiteService(object):

    def __init__(self, dropbox_user):
        self.dropbox_user = dropbox_user

    def create(self, website_data):
        if not website_data['domain'].endswith('.knownly.net'):
            quota_service = QuotaService(self.dropbox_user.django_user)
            if quota_service.at_or_over_custom_domain_quota():
                raise DropboxWebsiteError(
                    'The limit on custom domains for this '
                    'account has been reached.')

        website_data['dropbox_user'] = self.dropbox_user
        return DropboxSite.objects.create(**website_data)

    def upload_template(self, website):
        dropbox = Dropbox(self.dropbox_user.dropbox_token)

        try:
            # Request metadata for the planned website folder. An error
            # response is expected indicating that the folder does not exist
            db_path = '/%s' % website.domain
            metadata = dropbox.files_get_metadata(db_path)
            # If an ApiError is not raised then the folder exists
            logger.warning('Unexpected metadata - likely the folder exists: %s'
                           % metadata)
            raise DropboxWebsiteError('A website folder with the same '
                                      'name already exists in your Dropbox '
                                      'so we\'ve left that alone.')
        except ApiError as e:
            if e.error.get_path().is_not_found():
                # As expected, no website folder exists
                self._put_template_files(dropbox, website)
                # Fetch site metadata so we can track activation
                self._fetch_site_metadata(website)
        except DropboxWebsiteError as dwe:
            raise dwe
        except Exception:
            logger.exception('Unexpected error when retrieving folder '
                             'metadata prior to website folder creation.')
            raise DropboxWebsiteError(
                'An unexpected error occurred and we could not create a '
                'website folder in your Dropbox. Please create it '
                'manually at: %s' % db_path)

    def _put_template_files(self, dropbox, website):
        output = '<html>\n<head>\n  <title>Hello world</title>\n' \
                 + '</head>\n<body>\n  <h1>Hello world...</h1>\n' \
                 + '</body>\n</html>\n'

        # Upload the file to dropbox
        db_path = '/%s/index.html' % website.domain
        try:
            dropbox.files_upload(output, db_path)
        except DropboxException:
            logger.exception('Unexpected response from Dropbox '
                             'when putting website template files')
            raise DropboxWebsiteError(
                'An unexpected error occurred and we could not create a '
                'website folder in your Dropbox. Please try '
                'creating it manually at: %s' % db_path)

    def _fetch_site_metadata(self, website):
        try:
            fetch_website_folder_cursor.delay(website.id)
        except:
            logger.error('Error creating fetch_website_folder_cursor task')
