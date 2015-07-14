from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html

from knownly.console.models import DropboxUser, DropboxSite, ArchivedDropboxSite

class DropboxUserAdmin(ModelAdmin):
    list_display = ('display_name', 'email', 'get_date_activated')

    def get_date_activated(self, obj):
        return obj.date_activated or ''
    get_date_activated.short_description = 'Date activated'

class DropboxSiteAdmin(ModelAdmin):
    list_display = ('domain', 'dropbox_user', 'date_created', 'get_date_activated', 'visit_site')
    list_filter = ('dropbox_user',)
    readonly_fields = ('date_created', 'date_activated', 'dropbox_hash')

    def get_date_activated(self, obj):
        return obj.date_activated or ''
    get_date_activated.short_description = 'Date activated'

    def _get_url(self, obj):
        return 'http://%s' % obj.domain

    def visit_site(self, obj):
        url = self._get_url(obj)
        return format_html('<a href="%s">%s</a>' % (url, url))
    visit_site.allow_tags = True
    visit_site.short_description = 'Visit Knownly Site'

    def view_on_site(self, obj):
        return self._get_url(obj)

class ArchivedDropboxSiteAdmin(ModelAdmin):
    list_display = ('domain', 'dropbox_user', 'date_created', 'date_archived')
    list_filter = ('dropbox_user',)


admin.site.register(DropboxUser, DropboxUserAdmin)
admin.site.register(DropboxSite, DropboxSiteAdmin)
admin.site.register(ArchivedDropboxSite, ArchivedDropboxSiteAdmin)