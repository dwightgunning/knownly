from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.forms import ModelForm
from django.utils import timezone

from knownly.people.models import Person

class PersonAdminForm(ModelForm):

    class Meta:
        model = Person
        exclude = ()

    def clean_email(self):
        return self.cleaned_data['email'] or None

class PersonAdmin(ModelAdmin):
    form = PersonAdminForm
    list_display = ('email', 'name', 'first_name', 'last_name', 'twitter_id', 'website', 'source', 'tags')
    readonly_fields = ('created', 'updated')

    def get_readonly_fields(self, request, obj=None):
            if obj: # editing an existing object
                return self.readonly_fields + ('email',)
            return self.readonly_fields

    def save_model(self, request, obj, form, change):
        obj.update = timezone.now()
        obj.save()

admin.site.register(Person, PersonAdmin)
