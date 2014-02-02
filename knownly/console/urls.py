from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.views.generic import TemplateView

from knownly.console.views import IndexView, DropboxAuthStartView, DropboxAuthCompleteView, LogoutDropboxUserView

urlpatterns = patterns('',
	url(r'^$', IndexView.as_view(), name='index'),
	url(r'^signup/$', DropboxAuthStartView.as_view(), name='dropbox_auth_start'),
	url(r'^signup_complete/$', DropboxAuthCompleteView.as_view(), name='dropbox_auth_finish'),
	url(r'^logout/$', LogoutDropboxUserView.as_view(), name='logout'),
)
