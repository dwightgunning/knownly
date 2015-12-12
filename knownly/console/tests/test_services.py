from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from dropbox import Dropbox
from dropbox.users import FullAccount, Name
from mock import MagicMock, patch

from knownly.console.models import DropboxUser
from knownly.console.services import DropboxUserService


class TestDropboxUserService(TestCase):

    # New or existing DropboxUser?
    # If new --> Fetch Dropbox Account, Create and link a Django Account
    # If existing --> Validate the token
    # Return the DropboxUser and let the caller know whether they're brand new

    def test_get_or_create__new_db_user(self):
        test_db_user_id = '123456789'
        test_db_account_id = 'db:1232342342342342342342342342342342342'
        test_db_token = '123'
        test_db_email = 'tester@knownly.net'

        test_given_name = 'first'
        test_surname = 'last'
        test_db_name = Name(given_name=test_given_name, surname=test_surname)

        mock_db_client = Dropbox('arg')
        mock_db_client.users_get_current_account = \
            MagicMock(return_value=FullAccount(account_id=test_db_account_id,
                                               name=test_db_name,
                                               email=test_db_email))

        db_user_service = DropboxUserService(
            db_token=test_db_token, dropbox=mock_db_client)

        db_user, created = db_user_service.get_or_create(test_db_user_id)

        # verify the data
        self.assertTrue(created)
        self.assertEqual(db_user.user_id, test_db_user_id)
        self.assertEqual(db_user.account_id, test_db_account_id)
        self.assertEqual(db_user.dropbox_token, test_db_token)
        self.assertIsNotNone(db_user.django_user)
        self.assertFalse(db_user.django_user.has_usable_password())
        DropboxUser.objects.get(pk=db_user.pk)
        User.objects.get(username='db:%s' % db_user.pk,
                         email=test_db_email,
                         first_name=test_given_name,
                         last_name=test_surname)

        # verify the mock
        mock_db_client.users_get_current_account.assert_called_once_with()

    def test_get_or_create__existing_db_user_same_token(self):
        test_db_user_id = '1111111111'
        test_db_account_id = 'db:1232342342342342342342342342342342343'
        test_db_token = '1234'
        test_db_email = 'anotherr@knownly.net'

        test_db_user = DropboxUser.objects.create(
            user_id=test_db_user_id, account_id=test_db_account_id,
            dropbox_token=test_db_token)
        test_django_user = User.objects.create_user(
            username='db:%s' % test_db_user, email=test_db_email,
            password='hello')
        test_db_user.django_user = test_django_user
        test_db_user.save(update_fields=['django_user'])

        db_user_service = DropboxUserService(db_token=test_db_token)
        db_user, created = db_user_service.get_or_create(test_db_user_id)

        # verify the data
        self.assertFalse(created)
        self.assertEqual(db_user, test_db_user)
        self.assertEqual(db_user.django_user, test_django_user)
        self.assertEqual(db_user.dropbox_token, test_db_token)

    @patch('knownly.console.tasks.refresh_website_bearer_tokens_for_user'
           '.delay')
    def test_get_or_create__existing_db_user_new_token(self, mock_delay):
        test_db_user_id = '222222222'
        test_db_account_id = 'db:1232342342342342342342342342342342344'
        test_db_token = '1235'
        test_db_email = 'another2@knownly.net'

        test_new_db_token = '123456789'
        test_db_user = DropboxUser.objects.create(
            user_id=test_db_user_id, account_id=test_db_account_id,
            dropbox_token=test_db_token)
        test_django_user = User.objects.create_user(
            username='db:%s' % test_db_user, email=test_db_email, password='p')
        test_db_user.django_user = test_django_user
        test_db_user.save(update_fields=['django_user'])

        db_user_service = DropboxUserService(db_token=test_new_db_token)
        db_user, created = db_user_service.get_or_create(test_db_user_id)

        # verify the data
        self.assertFalse(created)
        self.assertEqual(db_user, test_db_user)
        self.assertEqual(db_user.django_user, test_django_user)
        self.assertEqual(db_user.dropbox_token, test_new_db_token)

        # verify the mock
        mock_delay.assert_called_once_with(db_user.id)

    @patch('knownly.console.tasks.refresh_website_bearer_tokens_for_user'
           '.delay', side_effect=Exception())
    def test_get_or_create__existing_db_user_new_token_and_celery_error(
            self, mock_delay):
        test_db_user_id = '333333333'
        test_db_account_id = 'db:1232342342342342342342342342342342345'
        test_db_token = '1236'
        test_db_email = 'another3@knownly.net'

        test_new_db_token = '123456789'
        test_db_user = DropboxUser.objects.create(
            user_id=test_db_user_id, account_id=test_db_account_id,
            dropbox_token=test_db_token)
        test_django_user = User.objects.create_user(
            username='db:%s' % test_db_user,
            email=test_db_email, password='hello')
        test_db_user.django_user = test_django_user
        test_db_user.save(update_fields=['django_user'])

        mock_db_client = Dropbox('arg')
        mock_db_client.users_get_current_account = \
            MagicMock(side_effect=Exception())
        db_user_service = DropboxUserService(db_token=test_new_db_token,
                                             dropbox=mock_db_client)
        db_user, created = db_user_service.get_or_create(test_db_user_id)

        # verify the data
        self.assertFalse(created)
        self.assertEqual(db_user, test_db_user)
        self.assertIsNotNone(db_user.django_user)
        self.assertEqual(db_user.django_user, test_django_user)
        self.assertEqual(db_user.dropbox_token, test_new_db_token)

        # verify the mock
        mock_delay.assert_called_once_with(db_user.id)

    # What if retrieving the DB account fails? It's all under a txn.
    def test_get_or_create__dropbox_get_user_full_account_with_errors(self):
        test_db_user_id = '444444444'
        test_db_token = 1237

        mock_db_client = Dropbox('arg')
        mock_db_client.users_get_current_account = \
            MagicMock(side_effect=Exception())

        db_user_service = DropboxUserService(
            db_token=test_db_token, dropbox=mock_db_client)

        try:
            db_user, created = db_user_service.get_or_create(test_db_user_id)
        except Exception:
            pass

        # verify the data
        with self.assertRaises(DropboxUser.DoesNotExist):
            DropboxUser.objects.get(user_id=test_db_user_id)

        # verify the mock
        mock_db_client.users_get_current_account.assert_called_once_with()

    # What if storing the django user fails? It's all under a txn.
    @patch('django.contrib.auth.models.User.objects.create_user',
           side_effect=IntegrityError())
    def test_get_or_create__create_django_user_error(self, create_user):
        test_db_user_id = '55555555'
        test_db_account_id = 'db:1232342342342342342342342342342342347'
        test_db_token = '1238'
        test_db_email = 'another8@knownly.net'

        test_given_name = 'first'
        test_surname = 'last'
        test_db_name = Name(given_name=test_given_name, surname=test_surname)

        mock_db_client = Dropbox('arg')
        mock_db_client.users_get_current_account = \
            MagicMock(return_value=FullAccount(
                account_id=test_db_account_id,
                name=test_db_name,
                email=test_db_email))

        db_user_service = DropboxUserService(
            db_token=test_db_token, dropbox=mock_db_client)

        with self.assertRaises(IntegrityError):
            db_user, created = db_user_service.get_or_create(test_db_user_id)

        # verify the data
        with self.assertRaises(DropboxUser.DoesNotExist):
            DropboxUser.objects.get(user_id=test_db_user_id)

        # verify the mock
        mock_db_client.users_get_current_account.assert_called_once_with()
