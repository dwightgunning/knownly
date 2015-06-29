import datetime
import json
import logging

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
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
    knownly_plan = forms.ChoiceField(KNOWNLY_PLANS)
    currency = forms.ChoiceField(choices=CURRENCIES)
    period = forms.ChoiceField(choices=BILLING_PERIODS)
    customer_type = forms.ChoiceField(
        choices=CustomerBillingDetails.CUSTOMER_TYPES)
    stripe_token = forms.CharField(required=False)
    name = forms.CharField(required=False)
    street_address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    post_code = forms.CharField(required=False)
    country = forms.ChoiceField(choices=Countries, required=False)
    vat_number = forms.CharField(required=False)
    cc_bin = forms.CharField(min_length=6, max_length=6)

    def clean(self):
        cleaned_data = super(SubscriptionPlanForm, self).clean()
        customer_type = cleaned_data.get('customer_type')

        if customer_type == CustomerBillingDetails.BUSINESS:
            country = cleaned_data.get('country')
            vat_number = cleaned_data.get('vat_number')
            
            if country in EU_VAT_COUNTRIES and not vat_number:
                msg = "VAT Number required for EU businesses."
                self.add_error('vat_number', msg)
