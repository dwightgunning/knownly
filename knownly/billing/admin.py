from django.contrib import admin
from django.contrib.admin import ModelAdmin

from knownly.billing.models import *

class StripeCustomerAdmin(ModelAdmin):
    list_display = ('user', 'stripe_customer_id', 'currency', 'created_at')
    readonly_fields = ('user', 'stripe_customer_id', 'currency', 'created_at')

class CustomerBillingDetailsAdmin(ModelAdmin):
	list_display = ('user', 'customer_type', 'country', 'vat_country')

class StripeEventAdmin(ModelAdmin):
	list_display = ('stripe_id', 'created_at', 'event_type')

admin.site.register(CustomerBillingDetails, CustomerBillingDetailsAdmin)
admin.site.register(StripeCustomer, StripeCustomerAdmin)
admin.site.register(StripeEvent, StripeEventAdmin)
