from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.views.generic import TemplateView

from knownly import console

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^', include('knownly.console.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^robots.txt$', TemplateView.as_view(template_name="static/robots.txt", content_type='text/plain')),
    )