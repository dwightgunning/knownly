# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254, unique=True, null=True, blank=True)),
                ('source', models.CharField(max_length=64)),
                ('first_name', models.CharField(max_length=64, blank=True)),
                ('last_name', models.CharField(max_length=64, blank=True)),
                ('name', models.CharField(max_length=128, blank=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('location', models.CharField(max_length=128, blank=True)),
                ('twitter_id', models.CharField(max_length=64, blank=True)),
                ('website', models.URLField(blank=True)),
                ('blog', models.URLField(blank=True)),
                ('hireable', models.NullBooleanField()),
                ('company', models.CharField(max_length=64, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('tags', jsonfield.fields.JSONField(blank=True)),
            ],
            options={
                'ordering': ['-updated'],
                'verbose_name_plural': 'people',
            },
        ),
    ]
