from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from knownly import plans
from knownly.plans.services import CustomerSubscriptionService

User = get_user_model()

@receiver(post_save, sender=User)
def user_saved(sender, **kwargs):
    if kwargs['created']:
        service = CustomerSubscriptionService(kwargs['instance'])
        service.create_or_update_subscription(plans.FREE,
        									  reason='Customer signup')
