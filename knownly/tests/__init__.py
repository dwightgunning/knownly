from django.test import Client, LiveServerTestCase, override_settings
from django.conf import settings
from django.contrib.auth import get_user_model

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from knownly import plans
from knownly.plans.models import CustomerSubscription

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
        self.selenium.find_element_by_id('primary-cta')


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
        self.selenium.get('%s%s' % (self.live_server_url,
                                    '/welcome/developers'))
        # Expect to see the primary cta
        self.selenium.find_element_by_id('primary-cta')

    def test_designers(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                    '/welcome/designers'))
        # Expect to see the primary cta
        self.selenium.find_element_by_id('primary-cta')

    def test_creatives(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                    '/welcome/learning-to-code'))
        # Expect to see the primary cta
        self.selenium.find_element_by_id('primary-cta')


@override_settings(SESSION_COOKIE_SECURE=False)
@override_settings(TEST=True)
class FreePlanSelectionTests(LiveServerTestCase):
    fixtures = ['knownly/console/fixtures/test_fixtures.json']

    @classmethod
    def setUpClass(cls):
        super(FreePlanSelectionTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(FreePlanSelectionTests, cls).tearDownClass()

    def setUp(self):
        client = Client()
        client.get(self.live_server_url)
        self.assertTrue(client.login(username='test@knownly.net',
                                     password='test'))
        cookie = client.cookies[settings.SESSION_COOKIE_NAME]
        self.selenium.get(self.live_server_url + '/admin/')
        self.selenium.add_cookie({'name': 'sessionid',
                                  'value': cookie.value,
                                  'secure': False,
                                  'path': '/'})
        self.selenium.refresh()

    def test_free_plan(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/signup/'))
        self.selenium.implicitly_wait(15)
        # Expect to see the primary cta
        self.selenium.find_element_by_id('plan-form-submit').click()

        # Expect the following view to be the Console page
        self.selenium.implicitly_wait(15)
        self.selenium.find_element_by_id('console')

        CustomerSubscription.objects.get(
            user=User.objects.get(username='test@knownly.net'),
            current_plan=plans.FREE)


@override_settings(SESSION_COOKIE_SECURE=False)
@override_settings(TEST=True)
class LitePlanSelectionTests(LiveServerTestCase):
    fixtures = ['knownly/console/fixtures/test_fixtures.json']

    @classmethod
    def setUpClass(cls):
        super(LitePlanSelectionTests, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LitePlanSelectionTests, cls).tearDownClass()

    def setUp(self):
        client = Client()
        client.get(self.live_server_url)
        self.assertTrue(client.login(username='test@knownly.net',
                                     password='test'))
        cookie = client.cookies[settings.SESSION_COOKIE_NAME]
        self.selenium.get(self.live_server_url + '/admin/')
        self.selenium.add_cookie({'name': 'sessionid',
                                  'value': cookie.value,
                                  'secure': False,
                                  'path': '/'})
        self.selenium.refresh()

    def test_lite_plan(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/signup/'))
        self.selenium.implicitly_wait(15)
        self.selenium.find_element_by_xpath(
            "//input[@type='radio' and @value='lite']").click()
        self.selenium.find_element_by_id("lite-plan-btn").click()
        self.selenium.implicitly_wait(15)

        # Find and populate the billing details form
        payment_details = self.selenium.find_element_by_id('payment-details')
        self.assertNotEqual(payment_details.value_of_css_property('display'),
                            'none')

        self.selenium.find_element_by_id(
            'id_card_number').send_keys('5555555555554444')
        self.selenium.find_element_by_id('id_expiry_month').send_keys('11')
        self.selenium.find_element_by_id('id_expiry_year').send_keys('2020')
        self.selenium.find_element_by_id('id_cvc').send_keys('111')

        self.selenium.find_element_by_id('id_name').send_keys('111')
        self.selenium.find_element_by_id('id_street_address').send_keys('111')
        self.selenium.find_element_by_id('id_city').send_keys('111')
        self.selenium.find_element_by_id('id_post_code').send_keys('111')
        Select(self.selenium.find_element_by_id('id_country')) \
            .select_by_value('NL')

        # Expect to see the primary cta
        self.selenium.implicitly_wait(15)
        self.selenium.find_element_by_id('plan-form-submit').click()

        # Expect the following view to be the Console page
        self.selenium.implicitly_wait(15)
        self.selenium.find_element_by_id('console')

        CustomerSubscription.objects.get(
            user=User.objects.get(username='test@knownly.net'),
            current_plan=plans.LITE)
