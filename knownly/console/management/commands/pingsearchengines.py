import urllib2

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Pings the search engines with our sitemaps'

    urls = ['http://www.google.com/webmasters/sitemaps/ping?sitemap=https://www.knownly.net/sitemap.xml',
    		'http://www.google.com/webmasters/sitemaps/ping?sitemap=https://www.knownly.net/sitemap.xml',
    		'http://www.bing.com/webmaster/ping.aspx?siteMap=https://www.knownly.net/sitemap.xml',
    		'http://www.bing.com/webmaster/ping.aspx?siteMap=https://www.knownly.net/community/sitemap.xml']

    def handle(self, *args, **options):
    	for url in self.urls:
			response = urllib2.urlopen(url)
			print '%s :: %s' % (url, response.code)
