from django.conf.urls import patterns, url

from knownly.vouchers import views

urlpatterns = patterns('',
                       url(r'^vouchers/$',
                           views.VoucherRedemptionView.as_view()),
                       url(r'^vouchers/(?P<pk>[0-9]+)/$',
                           views.VoucherRedemptionView.as_view()),
                       )
