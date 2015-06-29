from django.db import transaction

from knownly.plans.models import CustomerSubscription, CustomerSubscriptionHistory

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
			subscription = CustomerSubscription(user=self.user, current_plan=plan)

		subscription.save()
		return subscription

	@transaction.atomic
	def cancel_subscription(self, plan):
		raise NotImplementedError
