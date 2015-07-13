from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.views.generic import TemplateView

from knownly import console
from knownly.billing.views import stripe_webhook
from knownly.console.views import dropbox_webhook
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('knownly.console.urls')),
    url(r'^', include('knownly.landingpages.urls')),
    url(r'^', include('knownly.plans.urls')),
    url(r'^billing/hook/$', stripe_webhook, name='stripe-webhook'),
    url(r'^dropbox/hook/$', dropbox_webhook, name='dropbox-webhook'),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^robots.txt$', TemplateView.as_view(template_name="static/robots.txt", content_type='text/plain')),
    )
