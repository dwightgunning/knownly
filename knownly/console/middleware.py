import json
import redis
import urlparse

from django.conf import settings
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404

from dropbox import client 

from knownly.console.models import DropboxUser, DropboxSite

import logging
logger = logging.getLogger(__name__)


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

            resource_path = '/%s/%s' % (domain_to_match, request.path.lstrip("/"))
            if resource_path == domain or resource_path.endswith('/'):
                resource_path = '%sindex.html' % resource_path

            dropbox_resource = None
            try:
                r_server = redis.Redis('localhost', port=6380)
                dropbox_resource = r_server.get('knownly-django-%s' % resource_path)
            except redis.ConnectionError:
                logger.exception('Error connecting to redis-cache')

            if dropbox_resource:
                # logger.debug("Redis dropbox resource cache HIT!!!")
                resource = json.loads(dropbox_resource)
                dropbox_authentication = resource[0]
                dropbox_redirect_path = resource[1]
            else:
                # logger.debug("Redis dropbox resource cache MISS!!!")

                # Find the dropbox user that owns the domain
                try:
                    website = DropboxSite.objects.get(domain=domain_to_match)
                except DropboxSite.DoesNotExist:
                    return HttpResponsePermanentRedirect('https://www.knownly.net')
                
                #logger.debug('website recognised as being from user: %s' % website.dropbox_user)

                dropbox_client = client.DropboxClient(website.dropbox_user.dropbox_token)
                dropbox_path = "/files/%s%s" % (dropbox_client.session.root, client.format_path(resource_path))
                dropbox_url, dropbox_params, dropbox_headers = dropbox_client.request(dropbox_path, method='GET', content_server=True)
                
                #logger.debug('Dropbox url to file: %s' % dropbox_url)
                split_url = urlparse.urlsplit(dropbox_url)
                dropbox_redirect_path = split_url.path
                
                dropbox_authentication = dropbox_headers['Authorization']
                r_server.setex(name='knownly-django-%s' % resource_path,
                               time=60,
                               value=json.dumps((dropbox_authentication,
                                                 dropbox_redirect_path)))

            #logger.debug('redirect full path: %s' % dropbox_redirect_path)
            response = HttpResponse()
            response['Authorization'] = dropbox_authentication
            response['Accept-Language'] = request.META.get('HTTP_ACCEPT_LANGUAGE')
            response['X-Forwarded-For'] = request.META.get('HTTP_X_FORWARDED_FOR')
            response['User-Agent'] = request.META.get('HTTP_USER_AGENT')
            response['Accept'] = request.META.get('HTTP_ACCEPT')
            response['Accept-Encoding'] = request.META.get('HTTP_ACCEPT_ENCODING')
            response['X-Accel-Redirect'] = '/%s%s' % (settings.INTERNAL_REDIRECT_DIRECTORY, dropbox_redirect_path)

            #logger.debug('X-Accel-Redirect: %s' % response['X-Accel-Redirect'])
            return response
