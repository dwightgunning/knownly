from django.contrib import admin
from django.contrib.admin import ModelAdmin

from knownly.console.models import DropboxUser, DropboxSite

class DropboxUserAdmin(ModelAdmin):
    list_display = ('display_name', 'email', 'subscription_active')

class DropboxSiteAdmin(ModelAdmin):
    list_display = ('domain', 'dropbox_user')
    list_filter = ('dropbox_user',)


admin.site.register(DropboxUser, DropboxUserAdmin)
admin.site.register(DropboxSite, DropboxSiteAdmin)