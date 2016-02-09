from django.conf.urls import include, patterns, url

from knownly.api import views

urlpatterns = \
    patterns('',
             url(r'^api/logout/$',
                 views.LogoutView.as_view(), name='logout'),
             url(r'^api/auth/',
                 include('rest_framework.urls', namespace='rest_framework')),
             url(r'^api/directory-listing/(?P<path>.+)',
                 views.DirectoryListingView.as_view(),
                 name='directory-listing'))
