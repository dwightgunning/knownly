from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase

from knownly.console.middleware import SubdomainToDropboxMiddleware
from knownly.console.models import DropboxUser


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


class MiddlewareTests(TestCase):
    fixtures = ['test_fixtures.json']

    def setUp(self):
        self.middleware = SubdomainToDropboxMiddleware()
        self.request = HttpRequest()

    def test_custom_domain_website_does_not_exist(self):
        self.request.META['HTTP_HOST'] = 'unknown.net'

        response = self.middleware.process_request(self.request)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)

    def test_knownly_subdomain_website_does_not_exist(self):
        self.request.META['HTTP_HOST'] = 'unknown.knownly.net'

        response = self.middleware.process_request(self.request)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)

    def test_custom_domain_website_index(self):
        self.request.META['HTTP_HOST'] = 'customsite1.com'

        response = self.middleware.process_request(self.request)

        self.assertIsNotNone(response)
        self.assertEqual(response['X-ACCEL-REDIRECT'],
                         settings.INTERNAL_REDIRECT_DIRECTORY)
        self.assertEqual(response['Dropbox-API-Arg'],
                         '{\"path\": \"/%s/index.html\"}'
                         % self.request.META['HTTP_HOST'])

    def test_knownly_subdomain_website_index(self):
        self.request.META['HTTP_HOST'] = 'test1.knownly.net'

        response = self.middleware.process_request(self.request)

        self.assertIsNotNone(response)
        self.assertEqual(response['X-ACCEL-REDIRECT'],
                         settings.INTERNAL_REDIRECT_DIRECTORY)
        self.assertEqual(response['Dropbox-API-Arg'],
                         '{\"path\": \"/%s/index.html\"}'
                         % self.request.META['HTTP_HOST'])

    def test_knownly_website_request(self):
        request1 = HttpRequest()
        request1.META['HTTP_HOST'] = 'www.knownly.net'
        request2 = HttpRequest()
        request2.META['HTTP_HOST'] = 'localhost'
        request3 = HttpRequest()
        request3.META['HTTP_HOST'] = '127.0.0.1'

        for request in (request1, request2, request3):
            response = self.middleware.process_request(request)
            self.assertIsNone(response)
