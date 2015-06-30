from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.views.generic import TemplateView

from knownly.console import views as console_views
from knownly.landingpages import views as landingpages_views

urlpatterns = patterns('',
	url(r'^$', console_views.IndexView.as_view(), name='console'),
	url(r'^login/$', landingpages_views.DropboxAuthStartView.as_view(), name='login'),
	url(r'^create/$', console_views.CreateWebsiteView.as_view(), name='create_website'),
    url(r'^remove/$', console_views.RemoveWebsiteView.as_view(), name='remove_website'),
	url(r'^logout/$', console_views.LogoutDropboxUserView.as_view(), name='logout'),
    url(r'^support/$', console_views.TemplateView.as_view(template_name="console/support.html"), name='support'),
)
