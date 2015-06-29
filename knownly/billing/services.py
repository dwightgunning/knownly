import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

import stripe

from knownly.billing.errors import PaymentProviderError
from knownly.billing.models import \
    CustomerBillingDetails, StripeCustomer, StripeEvent

from knownly import plans

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

TRIAL_DAYS_ON_FIRST_PAID_PLAN = 14

class CustomerBillingService(object):

    def __init__(self, user):
        self.user = user

    def has_billing_details(self):
        return CustomerBillingDetails.objects.filter(user=user).exists()

    def get_billing_details(self):
        billing_details = CustomerBillingDetails.objects.filter(user=self.user)
        if billing_details:
            return billing_details.latest()
        else:
            raise CustomerBillingDetails.DoesNotExist()

    def update_billing_details(self, details):
        billing_details = CustomerBillingDetails(
            user=self.user,
            billing_currency=details['currency'],
            customer_type=details['customer_type'],
            name=details['name'],
            street_address=details['street_address'],
            city=details['city'],
            post_code=details['post_code'],
            country=details['country'],
            vat_id=details.get('vat_id', ''),
            ip_address=details['ip_address'],
            cc_bin=details['cc_bin'])
        billing_details.save()

        stripe_customer_service = StripeCustomerService(self.user)
        stripe_customer_service.create_or_update_customer(
            currency=details['currency'],
            stripe_token=details['stripe_token'])

        return billing_details

    def update_subscription(self, selected_plan, period):
        # Delegates straight to StripeCustomerService as 
        # we don't need to do anything with the billing periods
        billing_details = self.get_billing_details()

        stripe_customer_service = StripeCustomerService(self.user)
        stripe_customer_service.update_subscription(
            selected_plan, period, billing_details.billing_currency)


class StripeCustomerService(object):

    def __init__(self, user):
        self.user = user

    def create_or_update_customer(self, currency, stripe_token):
        try:
            customer = StripeCustomer.objects.get( \
                user=self.user, currency=currency)
        except StripeCustomer.DoesNotExist:
            customer = StripeCustomer(user=self.user, currency=currency)

        try:
            if customer.stripe_customer_id:
                stripe_customer = \
                    stripe.Customer.retrieve(customer.stripe_customer_id)
                stripe_customer.email = self.user.email
                stripe_customer.source = stripe_token
                stripe_customer.save()
            else:
                stripe_customer = stripe.Customer.create( \
                    source=stripe_token, email=self.user.email)
                customer.stripe_customer_id=stripe_customer['id']
                customer.save()

        except stripe.error.StripeError as se:
            logger.exception('Could not create stripe customer', se)
            raise PaymentProviderError('Error registering customer with payment provider', se)

        return stripe_customer

    def update_subscription(self, selected_plan, period, currency):
        stripe_customer = StripeCustomer.objects.get(user=self.user)

        plan_id = '%s-%s-%s' % (selected_plan, period, currency)

        customer = stripe.Customer.retrieve(stripe_customer.stripe_customer_id)
        if customer['subscriptions']['data']:
            current_subscription = customer['subscriptions']['data'][0]
            current_plan
            if current_plan != plan_id:
                try:
                    subscription = customer.subscriptions.retrieve(
                        current_subscription['id'])
                    subscription.plan = plan_id
                    subscription.save()
                except stripe.error.StripeError as se:
                    logger.exception('Stripe API Error while updating stripe '
                                     'customer (%s) subscription to: %s',
                                     stripe_customer.user, plan_id)
                    raise PaymentProviderError('Error updating customer '
                                               'subscription', se)
            else:
                logger.error('Invalid state: cannot update subscription to '
                             'the same plan')

        else:
            try:
                trial_end = timezone.now() + \
                    timedelta(days=TRIAL_DAYS_ON_FIRST_PAID_PLAN)
                customer.subscriptions.create(
                    plan=plan_id,trial_end=trial_end.strftime('%s'))
            except:
                logger.exception('Stripe API Error while creating stripe '
                                 'customer (%s) subscription to: %s',
                                 stripe_customer.user, plan_id)
                raise PaymentProviderError('Error updating customer '
                                           'subscription', se)


class StripeEventHandler(object):

    # TODO: Wrap in a celery task
    def handle_event(self, event_id):
        event = StripeEvent(stripe_id=event_id)
        try:
            resp = stripe.Event.retrieve(event_id)
            event.event_type = resp['type']
            event.timestamp = datetime.utcfromtimestamp(resp['created'])
            event.data = resp
        except stripe.error.StripeError as se:
            logger.exception("Stripe API Error")
        event.save()
