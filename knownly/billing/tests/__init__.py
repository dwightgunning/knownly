from django.contrib.auth import get_user_model
from django.test import TestCase

from knownly.billing.forms import SubscriptionPlanForm
from knownly.billing.models import CustomerBillingDetails
from knownly import plans


class SubscriptionPlanFormTest(TestCase):

    def test_basic_plan_fields_required(self):
        form = SubscriptionPlanForm(data={})

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.pop('knownly_plan'))
        self.assertFalse(form.errors)


    def test_free_plan(self):
        form_data = {'knownly_plan': plans.FREE}

        form = SubscriptionPlanForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_lite_fields_required(self):
        form = SubscriptionPlanForm(data={'knownly_plan': plans.LITE})
        form.is_valid()
        print "ERRORS: %s" % form.errors
        self.assertFalse(form.is_valid())
        
        self.assertTrue(form.errors.pop('customer_type'))
        self.assertTrue(form.errors.pop('period'))
        self.assertTrue(form.errors.pop('currency'))
        self.assertTrue(form.errors.pop('name'))
        self.assertTrue(form.errors.pop('street_address'))
        self.assertTrue(form.errors.pop('city'))
        self.assertTrue(form.errors.pop('post_code'))
        self.assertTrue(form.errors.pop('country'))
        self.assertTrue(form.errors.pop('cc_bin'))
        self.assertTrue(form.errors.pop('stripe_token'))
        self.assertFalse(form.errors)

    def test_lite_personal_fields_required(self):
        form = SubscriptionPlanForm(data={'knownly_plan': plans.LITE,
                                          'customer_type': CustomerBillingDetails.PERSONAL})

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.pop('period'))
        self.assertTrue(form.errors.pop('currency'))
        self.assertTrue(form.errors.pop('name'))
        self.assertTrue(form.errors.pop('street_address'))
        self.assertTrue(form.errors.pop('city'))
        self.assertTrue(form.errors.pop('post_code'))
        self.assertTrue(form.errors.pop('country'))
        self.assertTrue(form.errors.pop('cc_bin'))
        self.assertTrue(form.errors.pop('stripe_token'))
        self.assertFalse(form.errors)

    def test_lite_business_non_eu_fields_required(self):
        form = SubscriptionPlanForm(data={'knownly_plan': plans.LITE,
                                          'customer_type': CustomerBillingDetails.BUSINESS})

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.pop('period'))
        self.assertTrue(form.errors.pop('currency'))
        self.assertTrue(form.errors.pop('name'))
        self.assertTrue(form.errors.pop('street_address'))
        self.assertTrue(form.errors.pop('city'))
        self.assertTrue(form.errors.pop('post_code'))
        self.assertTrue(form.errors.pop('country'))
        self.assertTrue(form.errors.pop('cc_bin'))
        self.assertTrue(form.errors.pop('stripe_token'))
        self.assertFalse(form.errors)

    def test_lite_business_eu_fields_required(self):
        form = SubscriptionPlanForm(data={'knownly_plan': plans.LITE,
                                          'customer_type': CustomerBillingDetails.BUSINESS,
                                          'country': 'NL'})

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.pop('period'))
        self.assertTrue(form.errors.pop('currency'))
        self.assertTrue(form.errors.pop('name'))
        self.assertTrue(form.errors.pop('street_address'))
        self.assertTrue(form.errors.pop('city'))
        self.assertTrue(form.errors.pop('post_code'))
        self.assertTrue(form.errors.pop('cc_bin'))
        self.assertTrue(form.errors.pop('stripe_token'))
        self.assertTrue(form.errors.pop('vat_id'))
        self.assertFalse(form.errors)               

    def test_lite_monthly_usd_personal(self):
        form = SubscriptionPlanForm(data={'knownly_plan': plans.LITE,
                                          'customer_type': CustomerBillingDetails.PERSONAL,
                                          'period': 'monthly',
                                          'currency': 'usd',
                                          'stripe_token': 'abc',
                                          'name': 'Dwight Gunning',
                                          'street_address': 'van Tuyll van Serooskerkenweg 73i',
                                          'city': 'Amsterdam',
                                          'post_code': '1076JG',
                                          'country': 'NL',
                                          'cc_bin': '123456',
                                          })

        self.assertTrue(form.is_valid(), form.errors)
