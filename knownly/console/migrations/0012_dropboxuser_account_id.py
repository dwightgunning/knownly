# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-12 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0011_auto_20151208_0612'),
    ]

    operations = [
        migrations.AddField(
            model_name='dropboxuser',
            name='account_id',
            field=models.CharField(max_length=64, null=True, verbose_name='account id')
        ),
    ]