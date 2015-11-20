import logging

from django.contrib.auth import get_user_model
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse

from knownly.console.models import DropboxUser

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
