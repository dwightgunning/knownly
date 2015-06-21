import datetime
import unittest

from django.test import LiveServerTestCase
from django.conf import settings
from django.contrib.auth import get_user_model

from selenium.webdriver.firefox.webdriver import WebDriver

User = get_user_model()


class PublicPagesTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(PublicPagesTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(PublicPagesTests, cls).tearDownClass()

    def test_homepage(self):
        self.selenium.get(self.live_server_url)
        # Expect to see the primary cta
        self.selenium.find_element_by_id('btn-signup')


class LandingPageTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(LandingPageTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LandingPageTests, cls).tearDownClass()

    def test_developers(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/welcome/developers'))
        # Expect to see the primary cta
        self.selenium.find_element_by_id('primary-cta')

    def test_designers(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/welcome/designers'))
        # Expect to see the primary cta
        self.selenium.find_element_by_id('primary-cta')

    def test_creatives(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/welcome/creatives'))
        # Expect to see the primary cta
        self.selenium.find_element_by_id('primary-cta')
