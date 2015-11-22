import re

from django.contrib.auth.models import User
from rest_framework import serializers

from knownly.console.models import DropboxSite


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class DropboxSiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = DropboxSite
        fields = ('domain', 'date_created', 'date_activated', 'date_modified')

    def validate_domain(self, domain):
        if domain.endswith("knownly.com"):
            domain = self.cleaned_data['domain'] = domain[:-3] + "net"

        if DropboxSite.objects.filter(domain__iexact=domain).exists():
            raise serializers.ValidationError(
                'This domain has already been claimed. Please choose another.')

        valid_domains = re.compile(r'^[a-zA-Z\d-]{,63}'
                                   '(\.[a-zA-Z\d-]{,63})'
                                   '(\.[a-zA-Z\d-]{,63})?.$')
        if not valid_domains.match(domain):
            raise serializers.ValidationError(
                'This domain is invalid. Please try another.')

        if domain == 'knownly.net':
            raise serializers.ValidationError("Sorry, that one's ours.")

        return domain
