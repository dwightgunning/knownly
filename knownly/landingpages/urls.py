from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from knownly.landingpages import views as landingpage_views
from knownly.plans import views as plans_views


urlpatterns = patterns('',
	# Landing pages
	url(r'^welcome/developers/$', 
		TemplateView.as_view(template_name="landingpages/developers.html"),
		name='lp-developers'),
	url(r'^welcome/creatives/$', 
		TemplateView.as_view(template_name="landingpages/creatives.html"),
		name='lp-creatives'),
	url(r'^welcome/designers/$', 
		TemplateView.as_view(template_name="landingpages/designers.html"),
		name='lp-designers'),

	# Registration flow
	url(r'^signup/$',
		plans_views.PlansView.as_view(),
		name='signup'),
	url(r'^signup/begin/$',
		landingpage_views.DropboxAuthStartView.as_view(),
		name='dropbox_auth_start'),
	url(r'^signup/authorized/$',
		landingpage_views.DropboxAuthCompleteView.as_view(),
		name='dropbox_auth_finish'),
	url(r'^auth/choose-plan/$',
		landingpage_views.DropboxAuthSuccessView.as_view(new_customer=True),
		name='post_auth_new_customer'),
	url(r'^auth/continue/$',
		landingpage_views.DropboxAuthSuccessView.as_view(new_customer=False),
		name='post_auth_existing_customer'),
)