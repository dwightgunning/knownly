import urlparse
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from dropbox import client 

from knownly.console.models import DropboxUser, DropboxSite

class SubdomainToDropboxMiddleware(object):
	"""Middleware class that routes non "www" subdomain requests.
	"""

	def process_request(self, request):
		"""Returns an HTTP redirect response for requests including non-"www"
		subdomains.
		"""
		domain = request.META.get('HTTP_HOST') or request.META.get('SERVER_NAME')

		if domain.split(':')[0] in settings.ALLOWED_HOSTS:
			return None
		else:
			# Find the dropbox user that owns the domain
			website = get_object_or_404(DropboxSite, domain=domain)

			# Build up the dropbox request
			from_path = '/%s/%s' % (website.domain, request.path.strip("/"))
			if from_path.endswith('/'):
				from_path = '%sindex.html' % from_path

			dropbox_client = client.DropboxClient(website.dropbox_user.dropbox_token)
			dropbox_path = "/files/%s%s" % (dropbox_client.session.root, client.format_path(from_path))
			dropbox_url, dropbox_params, dropbox_headers = dropbox_client.request(dropbox_path, method='GET', content_server=True)
			
			split_url = urlparse.urlsplit(dropbox_url)
			dropbox_redirect_path = split_url.path

			response = HttpResponse()
			for i in dropbox_headers:
				response[i] = dropbox_headers[i]

			response['Accept-Language'] = request.META.get('HTTP_ACCEPT_LANGUAGE')
			response['X-Forwarded-For'] = request.META.get('HTTP_X_FORWARDED_FOR')
			response['User-Agent'] = request.META.get('HTTP_USER_AGENT')
			response['Accept'] = request.META.get('HTTP_ACCEPT')
			response['pragma'] = request.META.get('HTTP_PRAGMA')
			response['Cache-Control'] = request.META.get('HTTP_CACHE_CONTROL')
			response['Accept-Encoding'] = request.META.get('HTTP_ACCEPT_ENCODING')
			response['X-Accel-Redirect'] = '/%s%s' % (settings.INTERNAL_REDIRECT_DIRECTORY, dropbox_redirect_path)

			return response
