from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from knownly.vouchers.admin import VoucherRedemptionForm
from knownly.vouchers.models import Voucher, VoucherCampaign


class VoucherCampaignTest(TestCase):

    def test_create_voucher_campaign_no_dates(self):
        campaign = VoucherCampaign.objects.create(
            name='campaign with no dates')
        self.assertIsNotNone(campaign.pk)

    def test_create_voucher_campaign_with_end_date_before_start_date(self):
        campaign = VoucherCampaign(name='campaign',
                                   start_date=timezone.now() - timedelta(1),
                                   end_date=timezone.now() - timedelta(2))

        with self.assertRaises(ValidationError):
            campaign.full_clean()


class VoucherTest(TestCase):

    def setUp(self):
        self.campaign = VoucherCampaign.objects.create(
            name='campaign',
            start_date=timezone.now() - timedelta(1))

    def test_create_voucher_campaign_with_no_vouchers(self):
        with self.assertRaises(ValidationError):
            Voucher.objects.create(campaign=self.campaign,
                                   voucher_code='ABC123',
                                   total_available=0)


class VoucherRedemptionFormTest(TestCase):

    def setUp(self):
        self.campaign = VoucherCampaign.objects.create(
            name='campaign',
            start_date=timezone.now() - timedelta(1))
        self.campaign_no_start_date = VoucherCampaign.objects.create(
            name='campaign with no start')
        self.campaign_not_started = VoucherCampaign.objects.create(
            name='campaign not started',
            start_date=timezone.now() + timedelta(1))
        self.campaign_already_ended = VoucherCampaign.objects.create(
            name='campaign already ended',
            start_date=timezone.now() - timedelta(2),
            end_date=timezone.now() - timedelta(1))

        user_model = get_user_model()
        self.user1 = user_model.objects.create(username='1',
                                               email='email1@email.com',
                                               password='password')
        self.user2 = user_model.objects.create(username='2',
                                               email='email2@email.com',
                                               password='password')

    # Save a new voucher
    def test_new_voucher_redemption(self):
        voucher = Voucher.objects.create(campaign=self.campaign,
                                         voucher_code='voucher',
                                         total_available=1)

        redemption_form = VoucherRedemptionForm({'user': self.user1.pk,
                                                 'voucher': voucher.pk})
        self.assertTrue(redemption_form.is_valid(), redemption_form.errors)
        redemption = redemption_form.save()
        self.assertIsNotNone(redemption.pk)

    # Attempt to save a voucher with no more vouchers available
    def test_voucher_redemption_with_no_vouchers_available(self):
        voucher = Voucher.objects.create(campaign=self.campaign,
                                         voucher_code='voucher_code',
                                         total_available=1)

        redemption_form = VoucherRedemptionForm({'user': self.user1.pk,
                                                 'voucher': voucher.pk})
        self.assertTrue(redemption_form.is_valid(), redemption_form.errors)
        redemption = redemption_form.save()
        self.assertIsNotNone(redemption.pk)

        redemption_form = VoucherRedemptionForm({'user': self.user2.pk,
                                                 'voucher': voucher.pk})
        self.assertFalse(redemption_form.is_valid())
        self.assertEqual(redemption_form.errors.pop('voucher'),
                         ['This voucher has already been redeemed'])

    # Attempt to save a voucher where the campaign has ended
    def test_voucher_redemption_with_campaign_ended(self):
        voucher = Voucher.objects.create(campaign=self.campaign_already_ended,
                                         voucher_code='ended_voucher',
                                         total_available=2)

        redemption_form = VoucherRedemptionForm({'user': self.user1.pk,
                                                 'voucher': voucher.pk})
        self.assertFalse(redemption_form.is_valid())
        self.assertEqual(redemption_form.errors.pop('voucher'),
                         ['The associated campaign has ended'])

    # Attempt to save a voucher before the campaign has started
    def test_voucher_redemption_with_campaign_not_started(self):
        voucher = Voucher.objects.create(campaign=self.campaign_not_started,
                                         voucher_code='not_started_voucher',
                                         total_available=5)

        redemption_form = VoucherRedemptionForm({'user': self.user1.pk,
                                                 'voucher': voucher.pk})
        self.assertFalse(redemption_form.is_valid())
        self.assertEqual(redemption_form.errors.pop('voucher'),
                         ['The associated campaign has not started'])

    # Attempt to save a voucher before the campaign has started
    def test_voucher_redemption_with_campaign_no_start_date(self):
        voucher = Voucher.objects.create(campaign=self.campaign_no_start_date,
                                         voucher_code='not_started_voucher',
                                         total_available=5)

        redemption_form = VoucherRedemptionForm({'user': self.user1.pk,
                                                 'voucher': voucher.pk})
        self.assertFalse(redemption_form.is_valid())
        self.assertEqual(redemption_form.errors.pop('voucher'),
                         ['The associated campaign has not started'])
