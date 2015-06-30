# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0002_dropboxuser_django_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dropboxuser',
            name='subscription_active',
        ),
    ]
