import re

from django import forms

from knownly.console.models import DropboxSite


class WebsiteForm(forms.ModelForm):

    class Meta:
        model = DropboxSite
        fields = ['domain']
        domain = forms.CharField(
            error_messages={'required': 'Please enter a domain.'})

        def clean_domain(self):
            domain = self.cleaned_data['domain']

            if domain.endswith("knownly.com"):
                domain = domain[:-3] + "net"

            if DropboxSite.objects.filter(domain__iexact=domain).exists():
                raise forms.ValidationError('This domain has already been '
                                            'claimed. Please choose another.')

            valid_domains = re.compile(r'^[a-zA-Z\d-]{,63}'
                                       '(\.[a-zA-Z\d-]{,63})'
                                       '(\.[a-zA-Z\d-]{,63})?.$')
            if not valid_domains.match(domain):
                raise forms.ValidationError('This domain is invalid. '
                                            'Please try another.')

            if domain == 'knownly.net':
                raise forms.ValidationError("Sorry, that one's ours.")

            return domain

        def save(self, commit=True):
            instance = super(WebsiteForm, self).save(commit=False)
            instance.dropbox_user = self.dropbox_user
            if commit:
                instance.save()
            return instance
