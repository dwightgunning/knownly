from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html

from knownly.console.models import (ArchivedDropboxSite, DropboxSite,
                                    DropboxUser)


class DropboxUserAdmin(ModelAdmin):
    list_display = ('user_id', 'get_django_user_email', 'get_date_activated', )

    def get_django_user_email(self, obj):
        return obj.django_user.email or ''
    get_django_user_email.short_description = 'Django user'

    def get_date_activated(self, obj):
        return obj.date_activated or ''
    get_date_activated.short_description = 'Date activated'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DropboxSiteAdmin(ModelAdmin):
    list_display = ('domain', 'get_django_user_email', 'date_created',
                    'get_date_activated', 'get_visit_site')
    readonly_fields = ('date_created', 'date_activated')

    def get_date_activated(self, obj):
        return obj.date_activated or ''
    get_date_activated.short_description = 'Date activated'

    def get_django_user_email(self, obj):
        return obj.dropbox_user.django_user.email or ''
    get_django_user_email.short_description = 'Django user'

    def get_visit_site(self, obj):
        url = self._get_url(obj)
        return format_html('<a href="%s">%s</a>' % (url, url))
    get_visit_site.allow_tags = True
    get_visit_site.short_description = 'Visit Knownly Site'

    def _get_url(self, obj):
        return 'http://%s' % obj.domain

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ArchivedDropboxSiteAdmin(ModelAdmin):
    list_display = ('domain', 'dropbox_user', 'date_created', 'date_archived')

    def get_actions(self, request):
        #  Disable delete
        actions = super(ArchivedDropboxSiteAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(DropboxUser, DropboxUserAdmin)
admin.site.register(DropboxSite, DropboxSiteAdmin)
admin.site.register(ArchivedDropboxSite, ArchivedDropboxSiteAdmin)
