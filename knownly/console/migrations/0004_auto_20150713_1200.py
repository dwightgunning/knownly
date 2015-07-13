# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0003_remove_dropboxuser_subscription_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='archiveddropboxsite',
            name='date_activated',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='dropboxsite',
            name='date_activated',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
