# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0004_auto_20150713_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='dropboxuser',
            name='date_activated',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
