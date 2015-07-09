import urlparse
from django.conf import settings
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404

from dropbox import client 

from knownly.console.models import DropboxUser, DropboxSite

# Get an instance of a logger
# import logging
# logger = logging.getLogger(__name__)


class SubdomainToDropboxMiddleware(object):
	"""Middleware class that routes non "www" subdomain requests.
	"""

	def process_request(self, request):
		"""Returns an HTTP redirect response for requests including non-"www"
		subdomains.
		"""
		domain = request.META.get('HTTP_HOST') or request.META.get('SERVER_NAME')
		domain_to_match = domain.split(':')[0]

		if domain_to_match in ('www.knownly.net', '127.0.0.1', 'localhost'):
			#logger.debug('Serving: %s' % request.path)
			return None
		else:
			#logger.debug('Redirecting to dropbox: %s via website: %s' % (request.path, domain_to_match))

			# Find the dropbox user that owns the domain
			try:
				website = DropboxSite.objects.get(domain=domain_to_match)
			except DropboxSite.DoesNotExist:
				return HttpResponsePermanentRedirect('https://www.knownly.net')
			
			#logger.debug('website recognised as being from user: %s' % website.dropbox_user)

			# Build up the dropbox request
			from_path = '/%s/%s' % (website.domain, request.path.lstrip("/"))
			if from_path == domain or from_path.endswith('/'):
				from_path = '%sindex.html' % from_path

			dropbox_client = client.DropboxClient(website.dropbox_user.dropbox_token)
			dropbox_path = "/files/%s%s" % (dropbox_client.session.root, client.format_path(from_path))
			dropbox_url, dropbox_params, dropbox_headers = dropbox_client.request(dropbox_path, method='GET', content_server=True)
			
			#logger.debug('Dropbox url to file: %s' % dropbox_url)
			split_url = urlparse.urlsplit(dropbox_url)
			dropbox_redirect_path = split_url.path

			#logger.debug('redirect full path: %s' % dropbox_redirect_path)
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

			#logger.debug('X-Accel-Redirect: %s' % response['X-Accel-Redirect'])
			return response
