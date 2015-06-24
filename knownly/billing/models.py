from django.conf import settings
from django.db import models


class StripeCustomer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    customer_id = models.CharField(max_length=50)

    def __unicode__(self):
        return self.user.username
