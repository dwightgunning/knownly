from django.contrib import admin
from django.contrib.admin import ModelAdmin

from knownly.plans.models import CustomerSubscription, CustomerSubscriptionHistory

class CustomerSubscriptionAdmin(ModelAdmin):
    list_display = ('user', 'current_plan', 'active', 'created')
    readonly_fields = ('user', 'created')


class CustomerSubscriptionHistoryAdmin(ModelAdmin):
    list_display = ('user', 'timestamp', 'old_plan', 'new_plan', 'reason')
    readonly_fields = ('user', 'timestamp')

admin.site.register(CustomerSubscription, CustomerSubscriptionAdmin)
admin.site.register(CustomerSubscriptionHistory, CustomerSubscriptionHistoryAdmin)
