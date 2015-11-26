import logging
import StringIO

from django.contrib.auth import get_user_model
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse

from knownly.console.exceptions import DropboxWebsiteError
from knownly.console.models import DropboxSite, DropboxUser
from knownly.console.tasks import fetch_website_folder_metadata

logger = logging.getLogger(__name__)

User = get_user_model()


class DropboxUserService(object):

    def get_or_create(self, user_id, dropbox_token):
        dropbox_user, created = DropboxUser.objects.get_or_create(
            user_id=user_id, defaults={'dropbox_token': dropbox_token})

        if created or not dropbox_user.django_user:
            # Fetch the Dropbox user's account info
            try:
                client = DropboxClient(dropbox_user.dropbox_token)
                account_info = client.account_info()
            except ErrorResponse as e:
                logger.exception('Dropbox API Error', e)
            else:
                dropbox_user.django_user = self._create_user(account_info)
                dropbox_user.save()
        else:
            dropbox_user.dropbox_token = dropbox_token
            dropbox_user.save()

        return dropbox_user, created

    def _create_user(self, account_info):
        email = account_info['email']
        if 'name_details' in account_info:
            first_name = account_info['name_details'].get('given_name')
            last_name = account_info['name_details'].get('surname')
        else:
            first_name = ''
            last_name = ''
        random_password = User.objects.make_random_password()

        if User.objects.filter(username=email).exists():
            user = User.objects.get(username=email)
            user.username = account_info['uid'],
            user.first_name = first_name,
            user.last_name = last_name,
            user.password = random_password
            user.save()
        else:
            return User.objects.create_user(username=account_info['uid'],
                                            email=email,
                                            first_name=first_name,
                                            last_name=last_name,
                                            password=random_password)


class DropboxSiteService(object):

    def __init__(self, dropbox_user):
        self.dropbox_user = dropbox_user

    def create(self, website_data):
        # TODO: Check Quota
        website_data['dropbox_user'] = self.dropbox_user
        return DropboxSite.objects.create(**website_data)

    def upload_template(self, website):
        dropbox_client = DropboxClient(self.dropbox_user.dropbox_token)

        try:
            # Request metadata for the planned website folder. An error
            # response is expected indicating that the folder does not exist
            #
            # A file_limit of 2 is used to keep the request quick
            metadata = dropbox_client.metadata(website.domain, file_limit=2)
            logger.warning('Unexpected metadata when attempting to upload '
                           'website template website folder creation: %s'
                           % metadata)
            raise DropboxWebsiteError('A website folder with the same '
                                      'name already exists in your Dropbox '
                                      'so we\'ve left that alone.')
        except ErrorResponse as e:
            if e.status == 404:
                # As expected, no website folder exists
                self._put_template_files(dropbox_client, website)
            elif e.status == 406:
                # Dropbox API v1 returns a 406 if the file_limit is exceeded
                raise DropboxWebsiteError(
                    'A website folder with the same name already '
                    'exists in your Dropbox. We\'ve left it unchanged '
                    'and it will now be linked to your chosen domain.')
            else:
                logger.exception('Unexpected response from Dropbox '
                                 'when retrieving folder metadata prior to '
                                 'website folder creation.')
                raise DropboxWebsiteError(
                    'An error occurred and we could not create a '
                    'website folder in your Dropbox. Please try '
                    'creating it manually.')

        # Fetch site metadata so we can actively track website activation
        self._fetch_site_metadata(website)

    def _put_template_files(self, dropbox_client, website):
        # setup the file
        output = StringIO.StringIO()
        output.write('<html>\n<head>\n  <title>Hello world</title>\n'
                     '</head>\n<body>\n  <h1>Hello world...</h1>\n'
                     '</body>\n</html>\n')

        # Upload the file to dropbox
        try:
            dropbox_client.put_file('%s/index.html' % website.domain, output)
        except Exception:
            logger.exception('Unexpected response from Dropbox '
                             'when putting website template files')
            raise DropboxWebsiteError(
                'An error occurred and we could not create a '
                'website folder in your Dropbox. Please try '
                'creating it manually.')

    def _fetch_site_metadata(self, website):
        try:
            fetch_website_folder_metadata.delay(website.id)
        except:
            logger.error('Error creating fetch_website_folder_metadata task')
