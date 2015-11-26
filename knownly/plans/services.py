from django.db import transaction

from knownly import plans
from knownly.console.models import DropboxSite, DropboxUser
from knownly.plans.models import (CustomerSubscription,
                                  CustomerSubscriptionHistory)


class CustomerSubscriptionService(object):

    def __init__(self, user):
        self.user = user

    def get_current_subscription(self):
        return CustomerSubscription.objects.get(user=self.user)

    def has_current_subscription(self):
        return CustomerSubscription.objects.filter(user=self.user).exists()

    @transaction.atomic
    def create_or_update_subscription(self, plan, reason=''):
        if self.has_current_subscription():
            subscription = self.get_current_subscription()

            history_record = CustomerSubscriptionHistory(
                user=self.user,
                old_plan=subscription.current_plan,
                new_plan=plan,
                reason=reason)
            history_record.save()

            subscription.current_plan = plan
        else:
            subscription = CustomerSubscription(user=self.user,
                                                current_plan=plan)

        subscription.save()
        return subscription

    @transaction.atomic
    def cancel_subscription(self, plan):
        raise NotImplementedError


class QuotaService(object):

    quotas = {
        plans.FREE: {
            'custom_domains': 0,
            'page_views': 10000,
            'data_transfer': 1073741824
        },
        plans.LITE: {
            'custom_domains': 3,
            'page_views': 10000000,
            'data_transfer': 1073741824
        },
        plans.PREMIUM: {
            'custom_domains': 15,
            'page_views': 50000000,
            'data_transfer': 107374182400
        }
    }

    def __init__(self, user):
        self.user = user

    def custom_domain_limit(self):
        subscription_service = CustomerSubscriptionService(self.user)
        subscription = subscription_service.get_current_subscription()

        return self.quotas[subscription.current_plan]['custom_domains']

    def custom_domains_claimed(self):
        dropbox_user = DropboxUser.objects.get(django_user=self.user)
        return DropboxSite.objects.filter(dropbox_user=dropbox_user).count()
