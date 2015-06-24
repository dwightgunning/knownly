from django.conf import settings
from django.conf.urls import patterns, include, url, static
from django.contrib import admin
from django.views.generic import TemplateView

from knownly.billing import views

urlpatterns = patterns('',
    url(r'^plans/$', TemplateView.as_view(template_name="billing/plans.html"), name='current_plan'),
    url(r'^support/$', TemplateView.as_view(template_name="billing/upgrade.html"), name='account_activation'),
    url(r'^register/$', views.PaidPlanRegistrationView.as_view(), name='paid_plan_registration'),
)
