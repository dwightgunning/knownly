# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields
from decimal import Decimal
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerBillingDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('billing_currency', models.CharField(max_length=3, choices=[(b'eur', b'Euro \xe2\x82\xac'), (b'usd', b'US $')])),
                ('customer_type', models.CharField(max_length=3, choices=[(b'ppl', b'Personal'), (b'biz', b'Business')])),
                ('name', models.CharField(max_length=30)),
                ('street_address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('post_code', models.CharField(max_length=16)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('vat_id', models.CharField(max_length=30, blank=True)),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True)),
                ('cc_bin', models.CharField(max_length=6, validators=[django.core.validators.MinLengthValidator(6)])),
                ('vat_country_checked_at', models.DateTimeField(null=True, blank=True)),
                ('vat_country', django_countries.fields.CountryField(blank=True, max_length=2)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='CustomerInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('invoice_date', models.DateField()),
                ('invoice_number', models.CharField(max_length=20)),
                ('domestic_sequence_number', models.CharField(max_length=20)),
                ('billing_details', models.ForeignKey(to='billing.CustomerBillingDetails')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceLineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100)),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('invoice_currency', models.CharField(max_length=3, choices=[(b'eur', b'Euro \xe2\x82\xac'), (b'usd', b'US $')])),
                ('amount', models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('amount_local', models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('total_amount', models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('total_amount_local', models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('vat_rate', models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00')), django.core.validators.MaxValueValidator(Decimal('100.00'))])),
                ('vat_amount', models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('vat_amount_local', models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('vat_amount_customer', models.DecimalField(max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('invoice', models.ForeignKey(to='billing.CustomerInvoice')),
            ],
        ),
        migrations.CreateModel(
            name='StripeCustomer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_customer_id', models.CharField(max_length=50)),
                ('currency', models.CharField(max_length=3, choices=[(b'eur', b'Euro \xe2\x82\xac'), (b'usd', b'US $')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='StripeEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_id', models.CharField(max_length=64)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('event_type', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField()),
                ('data', models.TextField(blank=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='stripecustomer',
            unique_together=set([('user', 'stripe_customer_id')]),
        ),
    ]
