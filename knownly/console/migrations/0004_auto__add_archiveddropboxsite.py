# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ArchivedDropboxSite'
        db.create_table(u'console_archiveddropboxsite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dropbox_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['console.DropboxUser'])),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_archived', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'console', ['ArchivedDropboxSite'])


    def backwards(self, orm):
        # Deleting model 'ArchivedDropboxSite'
        db.delete_table(u'console_archiveddropboxsite')


    models = {
        u'console.archiveddropboxsite': {
            'Meta': {'object_name': 'ArchivedDropboxSite'},
            'date_archived': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'dropbox_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['console.DropboxUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'console.dropboxsite': {
            'Meta': {'object_name': 'DropboxSite'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '63'}),
            'dropbox_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['console.DropboxUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'console.dropboxuser': {
            'Meta': {'object_name': 'DropboxUser'},
            'account_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'dropbox_token': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['console']