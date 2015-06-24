import logging
import stripe

from django.conf import settings

from knownly.billing.models import StripeCustomer

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeCustomerService(object):

    def create_stripe_customer(self, user, stripe_token):        
        try:
            resp = stripe.Customer.create(card=stripe_token,
            							  email=user.email)

            customer, created = StripeCustomer.objects.get_or_create(
            	user=user, customer_id=resp['id'])
            customer.save()
        except stripe.error.StripeError as se:
            errors = self._errors.setdefault(NON_FIELD_ERRORS, ErrorList())
            errors.append(se.message)
            logger.exception("Could not create stripe customer: %s" % se)
            return None

        return customer

    def register_customer_for_plan(self, customer, plan):
    	pass
