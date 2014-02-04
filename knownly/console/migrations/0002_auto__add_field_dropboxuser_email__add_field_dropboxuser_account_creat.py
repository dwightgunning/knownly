# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DropboxUser.email'
        db.add_column(u'console_dropboxuser', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=75),
                      keep_default=False)

        # Adding field 'DropboxUser.account_created'
        db.add_column(u'console_dropboxuser', 'account_created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 2, 3, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'DropboxUser.subscription_active'
        db.add_column(u'console_dropboxuser', 'subscription_active',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DropboxUser.email'
        db.delete_column(u'console_dropboxuser', 'email')

        # Deleting field 'DropboxUser.account_created'
        db.delete_column(u'console_dropboxuser', 'account_created')

        # Deleting field 'DropboxUser.subscription_active'
        db.delete_column(u'console_dropboxuser', 'subscription_active')


    models = {
        u'console.dropboxsite': {
            'Meta': {'object_name': 'DropboxSite'},
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