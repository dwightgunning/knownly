from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.views.static import serve as serve_static

from knownly.billing.views import stripe_webhook
from knownly.console.views import dropbox_webhook
from knownly.sitemaps import SupportPageSitemap

admin.autodiscover()

sitemaps = {
    'static': SupportPageSitemap,
}

urlpatterns = \
    patterns('',
             url(r'^', include('knownly.api.urls')),
             url(r'^', include('knownly.console.urls')),
             url(r'^', include('knownly.landingpages.urls')),
             url(r'^', include('knownly.plans.urls')),

             url(r'^billing/hook/$', stripe_webhook, name='stripe-webhook'),
             url(r'^dropbox/hook/$', dropbox_webhook, name='dropbox-webhook'),
             url(r'^admin/', include(admin.site.urls)),

             url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
                 name='django.contrib.sitemaps.views.sitemap'),

             url(r'domains/', serve_static,
                 {'path': 'index.html',
                  'document_root': settings.STATIC_ROOT},
                 name='custom-statics'), )

if settings.DEBUG:
    urlpatterns += \
        patterns('',
                 url(r'^robots.txt$', TemplateView.as_view(
                     template_name="static/robots.txt",
                     content_type='text/plain')),
                 url(r'static/(?P<path>.*)$', serve_static,
                     {'document_root': settings.STATIC_ROOT},
                     name='custom-statics'), )
