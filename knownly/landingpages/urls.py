from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
	url(r'^developers/$', 
		TemplateView.as_view(template_name="landingpages/developers.html"),
		name='lp-developers'),
	url(r'^creatives/$', 
		TemplateView.as_view(template_name="landingpages/creatives.html"),
		name='lp-creatives'),
	url(r'^designers/$', 
		TemplateView.as_view(template_name="landingpages/designers.html"),
		name='lp-designers'),
)
