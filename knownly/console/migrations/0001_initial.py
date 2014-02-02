# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DropboxUser'
        db.create_table(u'console_dropboxuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('dropbox_token', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'console', ['DropboxUser'])

        # Adding model 'DropboxSite'
        db.create_table(u'console_dropboxsite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dropbox_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['console.DropboxUser'])),
            ('domain', self.gf('django.db.models.fields.CharField')(unique=True, max_length=63)),
        ))
        db.send_create_signal(u'console', ['DropboxSite'])


    def backwards(self, orm):
        # Deleting model 'DropboxUser'
        db.delete_table(u'console_dropboxuser')

        # Deleting model 'DropboxSite'
        db.delete_table(u'console_dropboxsite')


    models = {
        u'console.dropboxsite': {
            'Meta': {'object_name': 'DropboxSite'},
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '63'}),
            'dropbox_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['console.DropboxUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'console.dropboxuser': {
            'Meta': {'object_name': 'DropboxUser'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'dropbox_token': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['console']