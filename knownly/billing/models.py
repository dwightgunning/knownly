# -*- coding: latin-1 -*-

from decimal import Decimal

from django.core.validators import *
from django.conf import settings
from django.db import models
from django.utils import timezone

from django_countries.fields import CountryField

EUR = 'eur'
USD = 'usd'
CURRENCIES = (
    (EUR, 'Euro €'),
    (USD, 'US $'))


class CustomerBillingDetails(models.Model):
    PERSONAL = 'ppl'
    BUSINESS = 'biz'
    CUSTOMER_TYPES = (
        (PERSONAL, 'Personal'),
        (BUSINESS, 'Business'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(default=timezone.now)
    billing_currency = models.CharField(max_length=3, choices=CURRENCIES)
    customer_type = models.CharField(max_length=3, choices=CUSTOMER_TYPES)
    name = models.CharField(max_length=30)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    post_code = models.CharField(max_length=16)
    country = CountryField()
    vat_id = models.CharField(max_length=30, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    cc_bin = models.CharField(
        max_length=6,
        validators=[MinLengthValidator(6),])
    vat_country_checked_at = models.DateTimeField(blank=True, null=True)
    vat_country = CountryField(blank=True)

    class Meta:
        get_latest_by = 'created_at'

class CustomerInvoice(models.Model):
    # FK to immutable Billing Details ensures we retain customer billing details
    # at the time of invoicing.
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    billing_details = models.ForeignKey(CustomerBillingDetails)
    created_at = models.DateTimeField(default=timezone.now)
    invoice_date = models.DateField()
    invoice_number = models.CharField(max_length=20)
    domestic_sequence_number = models.CharField(max_length=20)


class InvoiceLineItem(models.Model):
    # Values are stored in the invoice currency.
    # Local values are in the local currency for your tax purposes.
    # We store the VAT also in the customer's currency for EU VAT compliance.
    invoice = models.ForeignKey(CustomerInvoice)
    description = models.CharField(max_length=100)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    invoice_currency = models.CharField(max_length=3, choices=CURRENCIES)
    amount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))])
    amount_local =  models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))])
    total_amount =  models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))])
    total_amount_local = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))])
    vat_rate =  models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), 
                    MaxValueValidator(Decimal('100.00')),])
    vat_amount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))])
    vat_amount_local = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))])
    vat_amount_customer = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))])


class StripeCustomer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    stripe_customer_id = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, choices=CURRENCIES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'stripe_customer_id')
        get_latest_by = 'created_at'

    def __unicode__(self):
        return self.user.username


class StripeEvent(models.Model):
    stripe_id = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)
    event_type = models.CharField(max_length=64)
    timestamp = models.DateTimeField()
    data = models.TextField(blank=True)
