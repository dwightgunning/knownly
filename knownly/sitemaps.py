from django.contrib import sitemaps
from django.core.urlresolvers import reverse

class SupportPageSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['console', 'lp-designers', 'lp-creatives', 'lp-founders',
        		'lp-startupweekend', 'lp-learning-to-code', 'lp-developers',
        		'login', 'support', ]

    def location(self, item):
        return reverse(item)
