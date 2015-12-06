from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField


class DropboxUser(models.Model):
    django_user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True)
    user_id = models.CharField(_('user id'), max_length=30, unique=True)
    dropbox_token = models.TextField()
    account_created = models.DateTimeField(default=timezone.now)
    date_activated = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.user_id


class DropboxSite(models.Model):
    dropbox_user = models.ForeignKey(DropboxUser)
    domain = models.CharField(max_length=63, unique=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_activated = models.DateTimeField(blank=True, null=True)
    date_modified = models.DateTimeField(blank=True, null=True)
    config = JSONField(default={})
    cursor = models.CharField(max_length=64, blank=True)

    def __unicode__(self):
        return u'%s' % self.domain


class ArchivedDropboxSite(models.Model):
    dropbox_user = models.ForeignKey(DropboxUser)
    domain = models.CharField(max_length=63)
    date_created = models.DateTimeField()
    date_activated = models.DateTimeField(blank=True, null=True)
    date_modified = models.DateTimeField(blank=True, null=True)
    config = JSONField(default={})
    date_archived = models.DateTimeField(default=timezone.now)
