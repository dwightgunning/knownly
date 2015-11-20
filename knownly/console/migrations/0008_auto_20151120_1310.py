# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0007_auto_20150713_1558'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dropboxuser',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='dropboxuser',
            name='email',
        ),
    ]
