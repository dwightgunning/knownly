from django.test import TestCase

from knownly.console.models import DropboxUser
from django.contrib.auth import get_user_model

class RegistrationTest(TestCase):
	fixtures = ['plans.json', ]

	def test_ok(self):
		self.assertTrue(True)
