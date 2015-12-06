from django.conf.urls import patterns, url

from knownly.console import views as console_views
from knownly.console.views import IndexView
from knownly.landingpages import views as landingpages_views

urlpatterns = \
    patterns('',
             url(r'^$', IndexView.as_view(), name='console'),
             url(r'^account/', IndexView.as_view()),
             url(r'^domains/', IndexView.as_view()),
             url(r'^websites/', IndexView.as_view()),
             url(r'^support/$',
                 console_views.TemplateView.as_view(
                     template_name="console/support.html"),
                 name='support'),

             url(r'^login/$',
                 landingpages_views.DropboxAuthStartView.as_view(),
                 name='login'),
             url(r'^logout/$',
                 console_views.LogoutDropboxUserView.as_view(),
                 name='logout'),

             url(r'^api/account/profile/$',
                 console_views.ProfileView.as_view(),
                 name='profile'),
             url(r'^api/dropboxsite/$',
                 console_views.DropboxSiteListCreateView.as_view(),
                 name='dropboxsitelist'),
             url(r'^api/dropboxsite/(?P<domain>.+)/$',
                 console_views.DropboxSiteRetrieveDestroyView.as_view(),
                 name='dropboxsite'), )
