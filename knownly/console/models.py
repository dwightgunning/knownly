from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

class DropboxUser(models.Model):
	user_id = models.CharField(_('user id'), max_length=30, unique=True)
	display_name = models.CharField(_('display name'), max_length=30)
	dropbox_token = models.TextField()

	def __unicode__(self):
		return u'%s' % self.display_name

class DropboxSite(models.Model):
	dropbox_user = models.ForeignKey(DropboxUser)
	domain = models.CharField(max_length=63, unique=True)

	def __unicode__(self):
		return u'%s' % self.domain