import re

from django.contrib.auth.models import User
from rest_framework import serializers, validators

from knownly.console.models import DropboxSite
from knownly.plans.models import CustomerSubscription
from knownly.plans.serializers import CustomerSubscriptionSerializer


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    email = serializers.EmailField(required=True, allow_blank=False)
    subscription = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'subscription')

    def get_subscription(self, obj):
        subscription = CustomerSubscription.objects.get(user=obj)
        return CustomerSubscriptionSerializer(subscription).data


class DropboxSiteSerializer(serializers.ModelSerializer):
    # Explicitly define domain field with a custom uniqueness validator
    # that returns a user friendly error message
    domain = serializers.CharField(
        validators=[validators.UniqueValidator(
            queryset=DropboxSite.objects.all(),
            message='This domain has already been claimed,'
                    ' please choose another.')]
    )

    class Meta:
        model = DropboxSite
        fields = ('domain', 'date_created', 'date_activated', 'date_modified')

    def validate_domain(self, domain):
        domain = domain.lower()

        if domain.endswith("knownly.com"):
            raise serializers.ValidationError(
                'Please use \'.net\' (unfortunately we don\'t own '
                'the .com yet).')

        if DropboxSite.objects.filter(domain__iexact=domain).exists():
            raise serializers.ValidationError(
                'This domain has already been claimed. Please choose another.')

        valid_domains = re.compile(r'^[a-zA-Z\d-]{,63}'
                                   '(\.[a-zA-Z\d-]{,63})'
                                   '(\.[a-zA-Z\d-]{,63})?.$')
        if not valid_domains.match(domain):
            raise serializers.ValidationError(
                'This domain is invalid. Please try another.')

        if domain in ['knownly.net', 'www.knownly.net']:
            raise serializers.ValidationError('Sorry, that one is ours.')

        return domain
