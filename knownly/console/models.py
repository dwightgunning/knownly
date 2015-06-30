from django.conf import settings
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

class DropboxUser(models.Model):
	django_user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True)
	user_id = models.CharField(_('user id'), max_length=30, unique=True)
	display_name = models.CharField(_('display name'), max_length=30)
	dropbox_token = models.TextField()
	email = models.EmailField()
	account_created = models.DateTimeField(auto_now_add=True) #TODO: Migrate to default=timezone.now

	def __unicode__(self):
		return u'%s' % self.display_name

class DropboxSite(models.Model):
	dropbox_user = models.ForeignKey(DropboxUser)
	domain = models.CharField(max_length=63, unique=True)
	date_created = models.DateTimeField(auto_now_add=True) #TODO: Migrate to default=timezone.now
	
	def __unicode__(self):
		return u'%s' % self.domain

class ArchivedDropboxSite(models.Model):
	dropbox_user = models.ForeignKey(DropboxUser)
	domain = models.CharField(max_length=63)
	date_created = models.DateTimeField()
	date_archived = models.DateTimeField(auto_now_add=True) #TODO: Migrate to default=timezone.now
