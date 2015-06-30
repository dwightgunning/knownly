from django.conf import settings
from django.db import models
from django.utils import timezone

from knownly import plans


class CustomerSubscription(models.Model):
	PLANS = (
		(plans.FREE, 'Free'),
		(plans.LITE, 'Lite'),
		(plans.PREMIUM, 'Premium'))

	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	current_plan = models.CharField(max_length=12, choices=PLANS)
	active = models.BooleanField(default=True)
	created = models.DateTimeField(default=timezone.now)


class CustomerSubscriptionHistory(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	timestamp = models.DateTimeField(default=timezone.now)
	old_plan = models.CharField(
		max_length=12,
		choices=CustomerSubscription.PLANS)
	new_plan = models.CharField(
		max_length=12,
		choices=CustomerSubscription.PLANS)
	reason = models.TextField()
