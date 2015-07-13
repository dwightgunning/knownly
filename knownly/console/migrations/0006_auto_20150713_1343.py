# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0005_dropboxuser_date_activated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archiveddropboxsite',
            name='date_archived',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='dropboxsite',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='dropboxuser',
            name='account_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
