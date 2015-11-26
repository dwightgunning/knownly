from rest_framework import serializers

from knownly.plans.models import CustomerSubscription
from knownly.plans.services import QuotaService


class CustomerSubscriptionSerializer(serializers.ModelSerializer):
    plan_quota = serializers.SerializerMethodField(read_only=True)
    at_or_over_custom_domain_quota = \
        serializers.SerializerMethodField(read_only=True)

    def get_plan_quota(self, obj):
        return QuotaService.quotas[obj.current_plan]

    def get_at_or_over_custom_domain_quota(self, obj):
        return QuotaService(obj.user).at_or_over_custom_domain_quota()

    class Meta:
        model = CustomerSubscription
        fields = ('current_plan', 'active', 'created', 'plan_quota',
                  'at_or_over_custom_domain_quota')
