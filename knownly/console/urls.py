from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.views.generic import TemplateView

from knownly.console import views

urlpatterns = patterns('',
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^login/$', views.DropboxAuthStartView.as_view(), name='login'),
	url(r'^signup/$', views.DropboxAuthStartView.as_view(), name='dropbox_auth_start'),
	url(r'^signup_complete/$', views.DropboxAuthCompleteView.as_view(), name='dropbox_auth_finish'),
	url(r'^create/$', views.CreateWebsiteView.as_view(), name='create_website'),
    url(r'^remove/$', views.RemoveWebsiteView.as_view(), name='remove_website'),
	url(r'^logout/$', views.LogoutDropboxUserView.as_view(), name='logout'),
    url(r'^support/$', views.TemplateView.as_view(template_name="console/support.html"), name='support'),
)
