from django.apps import AppConfig

default_app_config = 'knownly.billing.KnownlyBillingAppConfig'


class KnownlyBillingAppConfig(AppConfig):
 
    name = 'knownly.billing'
    verbose_name = 'Knownly Billing'
 
    def ready(self):
        import knownly.billing.signals
