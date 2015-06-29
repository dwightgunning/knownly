from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from knownly.billing.services import StripeCustomerService

User = get_user_model()

# @receiver(post_save, sender=User)
# def user_saved(sender, **kwargs):
	# print "Billing received signal: user_saved."
    # if kwargs['created']:
    #     stripe_customer_service = StripeCustomerService()
    #     stripe_customer_service.create(kwargs['instance'])
