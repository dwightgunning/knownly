import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver
from django.utils import timezone


class VoucherCampaign(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def clean(self):
        # Don't allow end-date before start-date
        if self.start_date and self.end_date and \
                self.end_date <= self.start_date:
            raise ValidationError(
                {'end_date': 'End date must be after start date.'})

    def __unicode__(self):
        return self.name


class Voucher(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    campaign = models.ForeignKey(VoucherCampaign)
    voucher_code = models.CharField(max_length=24, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    total_available = models.PositiveIntegerField(
        validators=[MinValueValidator(1)])

    def __unicode__(self):
        return self.voucher_code


@receiver(models.signals.pre_save, sender=Voucher)
def my_handler(sender, instance, *args, **kwargs):
    instance.full_clean()


class VoucherRedemption(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    voucher = models.ForeignKey(Voucher)
    redeemed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("user", "voucher"), )
