from django.contrib import admin
from django.contrib.admin import ModelAdmin

from knownly.console.models import DropboxUser, DropboxSite, ArchivedDropboxSite

class DropboxUserAdmin(ModelAdmin):
    list_display = ('display_name', 'email')

class DropboxSiteAdmin(ModelAdmin):
    list_display = ('domain', 'dropbox_user', 'date_created')
    list_filter = ('dropbox_user',)

class ArchivedDropboxSiteAdmin(ModelAdmin):
    list_display = ('domain', 'dropbox_user', 'date_created', 'date_archived')
    list_filter = ('dropbox_user',)


admin.site.register(DropboxUser, DropboxUserAdmin)
admin.site.register(DropboxSite, DropboxSiteAdmin)
admin.site.register(ArchivedDropboxSite, ArchivedDropboxSiteAdmin)