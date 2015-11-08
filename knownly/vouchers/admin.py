from django import forms
from django.contrib import admin
from django.utils import timezone

from knownly.vouchers import models


class VoucherRedemptionForm(forms.ModelForm):

    class Meta:
        model = models.VoucherRedemption
        fields = ['user', 'voucher', ]

    def clean_voucher(self):
        voucher = self.cleaned_data['voucher']

        # Check limit on the associated voucher
        vouchers_redeemed = \
            models.VoucherRedemption.objects.filter(voucher=voucher).count()
        if vouchers_redeemed >= voucher.total_available:
            raise forms.ValidationError(
                'This voucher has already been redeemed')

        if not voucher.campaign.start_date or \
                voucher.campaign.start_date > timezone.now().date():
            raise forms.ValidationError(
                'The associated campaign has not started')

        if voucher.campaign.end_date and \
                voucher.campaign.end_date < timezone.now().date():
            raise forms.ValidationError(
                'The associated campaign has ended')

        return voucher


class VoucherCampaignAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', )
    list_display = ('name', 'start_date', 'end_date')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('name', )

        return self.readonly_fields


class VoucherAdmin(admin.ModelAdmin):
    list_display = ('voucher_code', 'campaign')
    readonly_fields = ('created_at', )


class VoucherRedemptionAdmin(admin.ModelAdmin):
    form = VoucherRedemptionForm
    list_display = ('user', 'voucher', 'redeemed_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('voucher', 'redeemed_at')

        return self.readonly_fields


admin.site.register(models.VoucherCampaign, VoucherCampaignAdmin)
admin.site.register(models.Voucher, VoucherAdmin)
admin.site.register(models.VoucherRedemption, VoucherRedemptionAdmin)
