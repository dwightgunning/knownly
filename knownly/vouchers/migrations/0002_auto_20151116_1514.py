# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('vouchers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voucher',
            name='id',
        ),
        migrations.RemoveField(
            model_name='vouchercampaign',
            name='id',
        ),
        migrations.RemoveField(
            model_name='voucherredemption',
            name='id',
        ),
        migrations.AddField(
            model_name='voucher',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='vouchercampaign',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='voucherredemption',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True),
        ),
    ]
