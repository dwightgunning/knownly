from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError

from knownly.vouchers import models, permissions, serializers


class VoucherRedemptionView(generics.ListCreateAPIView):
    serializer_class = serializers.VoucherRedemptionSerializer
    permission_classes = (IsAuthenticated, permissions.IsLinkedToUser)
    max_paginate_by = 10

    def perform_create(self, serializer):
        voucher_code = self.request.data['voucher_code']
        try:
            voucher = models.Voucher.objects.get(voucher_code=voucher_code)
        except models.Voucher.DoesNotExist:
            raise ValidationError({'error': 'This voucher code is invalid.'})

        # Check limit on the associated voucher and that the user has
        # not already claimed the voucher
        vouchers_redeemed = \
            models.VoucherRedemption.objects.filter(voucher=voucher).count()

        if vouchers_redeemed >= voucher.total_available or \
            models.VoucherRedemption.objects.filter(user=self.request.user,
                                                    voucher=voucher).exists():
            raise ValidationError(
                {'error': 'This voucher has already been redeemed.'})

        serializer.save(user=self.request.user, voucher=voucher)

    def get_queryset(self):
        user = self.request.user
        return models.VoucherRedemption.objects.filter(user=user)
