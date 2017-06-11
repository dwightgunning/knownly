import logging

from rest_framework import status
from rest_framework.test import APITestCase

logger = logging.getLogger(__name__)


class DirectoryListingViewTests(APITestCase):
    fixtures = ['test_fixtures.json']

    def test_invalid_website(self):
        response = self.client.get('/api/directory-listing/www.nosite.com')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_directory(self):
        response = self.client.get(
            '/api/directory-listing/test1.knownly.net/invalid_directory')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_directory_not_found(self):
        response = self.client.get(
            '/api/directory-listing/test2.knownly.net/listed_directory')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TODO: Test valid directory that exists; e.g. test-time DI with Mox
