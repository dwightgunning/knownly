from django.conf.urls import patterns, url

from knownly.domains import views

urlpatterns = patterns('',
                       url(r'^$', views.DomainsView.as_view(), name='domains'),
                       url(r'^status/(?P<path>.*)$', views.proxy_to_mashape,
                           {'target_url':
                            'https://domainr.p.mashape.com/v2/status'},
                           name='domain_status'),
                       url(r'^search/(?P<path>.*)$', views.proxy_to_mashape,
                           {'target_url':
                            'https://domainr.p.mashape.com/v2/search'},
                           name='domain_search'), )
