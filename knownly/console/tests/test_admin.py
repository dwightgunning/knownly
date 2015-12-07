import logging

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.test import Client, LiveServerTestCase, TestCase, override_settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver

from knownly.console.admin import (ArchivedDropboxSiteAdmin, DropboxSiteAdmin,
                                   DropboxUserAdmin)
from knownly.console.models import (ArchivedDropboxSite, DropboxSite,
                                    DropboxUser)

logger = logging.getLogger(__name__)


class DropboxUserAdminTests(TestCase):
    fixtures = ['test_fixtures.json']

    def setUp(self):
        self.admin = DropboxUserAdmin(DropboxUser, AdminSite())
        self.request = HttpRequest()

    def test_user_email_column_headings(self):
        user_obj = DropboxUser.objects.all()[0]
        user_email_col_value = self.admin.get_django_user_email(user_obj)

        self.assertEqual(user_obj.django_user.email, user_email_col_value)

    def test_none_date_activated_column(self):
        user_obj = DropboxUser.objects.get(user_id='436232319768')
        date_activated_col_value = self.admin.get_date_activated(user_obj)

        self.assertIsNone(user_obj.date_activated)
        self.assertEqual(date_activated_col_value, '')

    def test_date_activated_column(self):
        user_obj = DropboxUser.objects.get(user_id='436389768')
        date_activated_col_value = self.admin.get_date_activated(user_obj)

        self.assertEqual(date_activated_col_value, user_obj.date_activated)

    def test_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(self.request))

    def test_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(self.request))


class DropboxUserAdminSeleniumTests(TestCase):
    pass


class DropboxSiteAdminUnitTests(TestCase):
    fixtures = ['test_fixtures.json']

    def setUp(self):
        self.admin = DropboxSiteAdmin(DropboxSite, AdminSite())
        self.request = HttpRequest()

    def test_read_only_fields(self):
        self.assertEqual(self.admin.readonly_fields,
                         ('date_created', 'date_activated',))

    def test_user_email_column_headings(self):
        site_obj = DropboxSite.objects.get(domain='customsite2.com')
        site_user_email_col_value = self.admin.get_django_user_email(site_obj)

        self.assertEqual(site_obj.dropbox_user.django_user.email,
                         site_user_email_col_value)

    def test_none_date_activated_column(self):
        site_obj = DropboxSite.objects.get(domain='customsite2.com')
        date_activated_col_value = self.admin.get_date_activated(site_obj)

        self.assertIsNone(site_obj.date_activated)
        self.assertEqual(date_activated_col_value, '')

    def test_date_activated_column(self):
        site_obj = DropboxSite.objects.get(domain='customsite3.com')
        date_activated_col_value = self.admin.get_date_activated(site_obj)

        self.assertEqual(date_activated_col_value, site_obj.date_activated)

    def test_visit_site_column(self):
        site_obj = DropboxSite.objects.get(domain='customsite3.com')
        visit_site_col_value = self.admin.get_visit_site(site_obj)

        self.assertEqual(visit_site_col_value,
                         '<a href="http://customsite3.com">'
                         'http://customsite3.com</a>')

    def test_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(self.request))

    def test_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(self.request))


class DropboxSiteAdminSeleniumTests(TestCase):
    pass


class ArchivedDropboxSiteAdminUnitTests(TestCase):
    fixtures = ['test_fixtures.json']

    def setUp(self):
        self.admin = ArchivedDropboxSiteAdmin(ArchivedDropboxSite, AdminSite())
        self.request = HttpRequest()

    def test_list_view_fields(self):
        self.assertEqual(self.admin.list_display,
                         ('domain', 'dropbox_user', 'date_created',
                          'date_archived'))

    def test_delete_permission(self):
        self.assertFalse(self.admin.has_delete_permission(self.request))

    def test_add_permission(self):
        self.assertFalse(self.admin.has_add_permission(self.request))


@override_settings(SESSION_COOKIE_SECURE=False)
@override_settings(TEST=True)
class ArchivedDropboxSiteAdminSeleniumTests(LiveServerTestCase):
    fixtures = ['knownly/console/fixtures/test_fixtures.json']

    @classmethod
    def setUpClass(cls):
        super(ArchivedDropboxSiteAdminSeleniumTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(ArchivedDropboxSiteAdminSeleniumTests, cls).tearDownClass()

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

    def test_archived_dropbox_site_list_view(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                    '/admin/console/archiveddropboxsite/'))

        for col_name in ('domain', 'dropbox_user',
                         'date_created', 'date_archived'):
            self.selenium.find_element_by_xpath(
                '//table[@id=\'result_list\']/thead/tr/'
                'th[contains(@class, \'column-%s\')]' % col_name)

        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_class_name('addlink')

        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(
                '//select[@name=\'action\']/option'
                '[@value=\'delete_selected\']')
