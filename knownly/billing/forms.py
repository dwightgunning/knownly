import datetime
import json
import logging

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList

PROFESSIONAL_EUR_PLAN = 'pro-eur'
PREMIUM_EUR_PLAN = 'premium-eur'
FREE = 'free'

PLANS = (
	('free', 'Free'),
	('professional-eur', 'Professional'),
	('premium-eur', 'Premium'))

class SubscriptionPlanForm(forms.Form):
    email = forms.EmailField()
    plan = forms.ChoiceField(choices=PLANS)
    stripe_token = forms.CharField(required=False)
    name = forms.CharField(required=False)
    street_address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    country = forms.CharField(required=False)
    vat_number = forms.CharField(required=False)
