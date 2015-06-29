from django.conf import settings
from django.conf.urls import patterns, include, url, static

from knownly.plans import views

urlpatterns = patterns('',
	url(r'^choose-plan/$',
		views.PlansView.as_view(),
		name='choose-plan'),
)
