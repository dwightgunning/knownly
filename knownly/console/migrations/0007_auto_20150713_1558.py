# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0006_auto_20150713_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='archiveddropboxsite',
            name='date_modified',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='archiveddropboxsite',
            name='dropbox_hash',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='dropboxsite',
            name='date_modified',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='dropboxsite',
            name='dropbox_hash',
            field=models.CharField(max_length=64, blank=True),
        ),
    ]
