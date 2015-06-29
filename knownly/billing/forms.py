import datetime
import json
import logging

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList

from django_countries import Countries

from knownly.billing.models import CURRENCIES, CustomerBillingDetails
from knownly import plans

KNOWNLY_PLANS = (
    (plans.FREE, 'Free'),
    (plans.LITE, 'Lite'),
    (plans.PREMIUM, 'Premium'))

BILLING_PERIODS = (
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'))

EU_VAT_COUNTRIES = ['BE', 'EL', 'LT', 'PT', 'BG', 'ES', 'LU', 'RO', 'CZ', \
    'FR', 'HU', 'SI', 'DK', 'HR', 'MT', 'SK', 'DE', 'IT', 'NL', \
    'FI', 'EE', 'CY', 'AT', 'SE', 'IE', 'LV', 'PL', 'UK']


class SubscriptionPlanForm(forms.Form):
    error_css_class = 'text-danger'

    knownly_plan = forms.ChoiceField(KNOWNLY_PLANS, required=True)
    currency = forms.ChoiceField(choices=CURRENCIES, required=False)
    period = forms.ChoiceField(choices=BILLING_PERIODS, required=False)
    customer_type = forms.ChoiceField(
        choices=CustomerBillingDetails.CUSTOMER_TYPES, required=False)
    stripe_token = forms.CharField(required=False)
    name = forms.CharField(required=False)
    street_address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    post_code = forms.CharField(required=False)
    country = forms.ChoiceField(choices=Countries, required=False)
    vat_id = forms.CharField(required=False)
    cc_bin = forms.CharField(min_length=6, max_length=6, required=False)

    def clean(self):
        cleaned_data = super(SubscriptionPlanForm, self).clean()

        if cleaned_data.get('knownly_plan') in [plans.LITE, plans.PREMIUM]:
            cc_processing_message = 'Error processing credit card.'
            required_field_message = 'Required field.'

            non_cc_reqd_fields = ['customer_type', 'currency', 'period',
                                  'name', 'street_address', 'city', 
                                  'post_code', 'country']

            for field_name in non_cc_reqd_fields:
                if not cleaned_data.get(field_name, None):
                    self.add_error(field_name, 
                                   ValidationError(required_field_message, 
                                                   {'code': 'required'}))

            if not cleaned_data.get('stripe_token', None):
                self.add_error('stripe_token', 
                               ValidationError(cc_processing_message,
                                               {'code': 'cc_processing'}))
            if not cleaned_data.get('cc_bin', None):
                self.add_error('cc_bin',
                               ValidationError(cc_processing_message,
                                               {'code': 'cc_processing'}))

            customer_type = cleaned_data.get('customer_type')
            if customer_type == CustomerBillingDetails.BUSINESS:
                country = cleaned_data.get('country')
                vat_id = cleaned_data.get('vat_id')
                
                if country in EU_VAT_COUNTRIES and not vat_id:
                    message = "VAT ID required for EU businesses."
                    self.add_error('vat_id', ValidationError(message, {'code': 'required'}))
