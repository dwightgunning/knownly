from rest_framework import serializers

from knownly.vouchers import models


class CampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.VoucherCampaign
        fields = ('uuid', 'name', )


class VoucherSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer()

    class Meta:
        model = models.Voucher
        exclude = ('total_available', 'created_at')
        depth = 1


class VoucherRedemptionSerializer(serializers.ModelSerializer):
    voucher = VoucherSerializer(required=False)

    class Meta:
        model = models.VoucherRedemption
        exclude = ('user', )
        read_only_fields = ('uuid', 'redeemed_at')
        depth = 1
