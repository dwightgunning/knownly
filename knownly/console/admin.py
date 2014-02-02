from django.contrib import admin

from knownly.console.models import DropboxUser, DropboxSite

admin.site.register(DropboxUser)
admin.site.register(DropboxSite)