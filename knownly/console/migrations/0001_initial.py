# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivedDropboxSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=63)),
                ('date_created', models.DateTimeField()),
                ('date_archived', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DropboxSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(unique=True, max_length=63)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DropboxUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.CharField(unique=True, max_length=30, verbose_name='user id')),
                ('display_name', models.CharField(max_length=30, verbose_name='display name')),
                ('dropbox_token', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('account_created', models.DateTimeField(auto_now_add=True)),
                ('subscription_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='dropboxsite',
            name='dropbox_user',
            field=models.ForeignKey(to='console.DropboxUser'),
        ),
        migrations.AddField(
            model_name='archiveddropboxsite',
            name='dropbox_user',
            field=models.ForeignKey(to='console.DropboxUser'),
        ),
    ]
