from django.test import TestCase

from knownly.console.models import DropboxUser, DropboxSite
from knownly.console.services import DropboxUserService

class DropboxUserTests(TestCase):
	fixtures = ['test_fixtures.json']

	def test_has_activated_website_true(self):
		user = DropboxUser.objects.get(
			django_user__email="activated_website_user@test.com")
		self.assertTrue(user.date_activated)

	def test_has_activated_website_false(self):
		user = DropboxUser.objects.get(
			django_user__email="unactivated_website_user@test.com")
		self.assertIsNone(user.date_activated)