from django.conf.urls import patterns, url

from knownly.console import views as console_views
from knownly.landingpages import views as landingpages_views

urlpatterns = \
    patterns('',
             url(r'^login/$',
                 landingpages_views.DropboxAuthStartView.as_view(),
                 name='login'),
             url(r'^logout/$',
                 console_views.LogoutDropboxUserView.as_view(),
                 name='logout'),

             url(r'^support/$',
                 console_views.TemplateView.as_view(
                     template_name="console/support.html"),
                 name='support'),

             url(r'^api/account/profile/$',
                 console_views.ProfileView.as_view(),
                 name='profile'),
             url(r'^api/dropboxsite/$',
                 console_views.DropboxSiteListCreateView.as_view(),
                 name='dropboxsitelist'),
             url(r'^api/dropboxsite/(?P<domain>.+)/$',
                 console_views.DropboxSiteRetrieveDestroyView.as_view(),
                 name='dropboxsite')
             )
