from django.apps import AppConfig

default_app_config = 'knownly.plans.KnownlyPlansAppConfig'

FREE = 'free'
LITE = 'lite'
PREMIUM = 'premium'

 
class KnownlyPlansAppConfig(AppConfig):
 
    name = 'knownly.plans'
    verbose_name = 'Knownly Plans'
 
    def ready(self):
        import knownly.plans.signals
