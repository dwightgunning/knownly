# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True)),
                ('voucher_code', models.CharField(unique=True, max_length=24)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('total_available', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
            ],
        ),
        migrations.CreateModel(
            name='VoucherCampaign',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='VoucherRedemption',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True)),
                ('redeemed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('voucher', models.ForeignKey(to='vouchers.Voucher')),
            ],
        ),
        migrations.AddField(
            model_name='voucher',
            name='campaign',
            field=models.ForeignKey(to='vouchers.VoucherCampaign'),
        ),
        migrations.AlterUniqueTogether(
            name='voucherredemption',
            unique_together=set([('user', 'voucher')]),
        ),
    ]
