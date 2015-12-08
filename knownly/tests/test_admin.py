import logging

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import Client, LiveServerTestCase, TestCase, override_settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver

from knownly.admin import DjangoUserAdmin

logger = logging.getLogger(__name__)


class DjangoUserAdminUnitTests(TestCase):
    fixtures = ['test_fixtures.json']

    def setUp(self):
        self.admin = DjangoUserAdmin(User, AdminSite())
        self.request = HttpRequest()

    def test_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(self.request))

    def test_list_view_fields(self):
        self.assertEqual(self.admin.list_display,
                         ('username', 'email', 'first_name', 'last_name',
                          'is_staff', 'date_joined'))


@override_settings(SESSION_COOKIE_SECURE=False)
@override_settings(TEST=True)
class DjangoUserAdminSeleniumTests(LiveServerTestCase):
    fixtures = ['knownly/console/fixtures/test_fixtures.json']

    @classmethod
    def setUpClass(cls):
        super(DjangoUserAdminSeleniumTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(DjangoUserAdminSeleniumTests, cls).tearDownClass()

    def setUp(self):
        client = Client()
        client.get(self.live_server_url)
        self.assertTrue(client.login(username='admin@knownly.net',
                                     password='test'))
        cookie = client.cookies[settings.SESSION_COOKIE_NAME]
        self.selenium.get(self.live_server_url + '/admin/')
        self.selenium.add_cookie({'name': 'sessionid',
                                  'value': cookie.value,
                                  'secure': False,
                                  'path': '/'})
        self.selenium.refresh()

    def test_auth_user_list_view(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/auth/user/'))

        for col_name in ('username', 'email', 'first_name', 'last_name',
                         'is_staff', 'date_joined'):
            self.selenium.find_element_by_xpath(
                '//table[@id=\'result_list\']/thead/tr/'
                'th[contains(@class, \'column-%s\')]' % col_name)

        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(
                '//select[@name=\'action\']/option'
                '[@value=\'delete_selected\']')
