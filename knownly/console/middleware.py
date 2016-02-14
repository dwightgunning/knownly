import json
import logging

import redis
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect

from knownly.console.models import DropboxSite

logger = logging.getLogger(__name__)


class SubdomainToDropboxMiddleware(object):

    def process_request(self, request):
        host = request.META.get('HTTP_HOST') or request.META.get('SERVER_NAME')
        domain = host.split(':')[0].lower()

        if domain in ('www.knownly.net', '127.0.0.1', 'localhost',
                      'testserver'):
            logger.debug('Serving knownly site.')
            return None
        else:
            logger.debug('Serving hosted site: %s%s' % (domain, request.path))
            return self.serve_hosted_website(request, domain)

    def serve_hosted_website(self, request, domain):
        full_path = '/%s/%s' % (domain, request.path.lstrip("/"))
        if full_path == domain or full_path.endswith('/'):
            # default to serving index.html
            full_path = '%sindex.html' % full_path

        db_auth_header_redis_key = 'db-bearer--%s' % domain
        db_api_auth_header = None
        try:
            r_server = redis.Redis('localhost', port=6380)
            db_api_auth_header = r_server.get(db_auth_header_redis_key)
        except redis.ConnectionError:
            logger.error('Error connecting to redis-cache')

        if not db_api_auth_header:
            try:
                website = DropboxSite.objects.get(domain__iexact=domain)
            except DropboxSite.DoesNotExist:
                # TODO: Serve a custom "this domain is linked with Knownly
                # but is no longer available"
                return HttpResponseRedirect('https://www.knownly.net')

            db_api_auth_header = 'Bearer %s' % \
                website.dropbox_user.dropbox_token

        # Generate DB headers
        db_api_arg_header = json.dumps({'path': full_path})

        # Cache the auth header for the domain
        if r_server:
            try:
                r_server.setex(name=db_auth_header_redis_key,
                               time=86400,
                               value=db_api_auth_header)
            except redis.ConnectionError:
                logger.error('Error connecting to redis-cache')

        if settings.DJANGO_PROXY_KNOWNLY_WEBSITES:
            logger.warn('Django proxying the knownly website.')
            return self._proxy_request(request,
                                       full_path,
                                       db_api_auth_header,
                                       db_api_arg_header)
        else:
            return self._x_accel_redirect(request,
                                          full_path,
                                          db_api_auth_header,
                                          db_api_arg_header)

    def _proxy_request(self, request, full_path, db_api_auth_header,
                       db_api_arg_header):
        import mimetypes
        import requests

        headers = {
            'Authorization': db_api_auth_header,
            'Dropbox-API-Arg': db_api_arg_header,
            'Accept-Language': request.META.get('HTTP_ACCEPT_LANGUAGE'),
            'User-Agent': request.META.get('HTTP_USER_AGENT'),
            'Accept': request.META.get('HTTP_ACCEPT'),
            'Accept-Encoding': request.META.get('HTTP_ACCEPT_ENCODING'),
        }

        mime_type = mimetypes.MimeTypes().guess_type(full_path)[0]

        r = requests.get('https://content.dropboxapi.com/2/files/download',
                         headers=headers, stream=True)

        response = HttpResponse(r.raw.read(),
                                status=r.status_code,
                                content_type=mime_type)

        return response

    def _x_accel_redirect(self, request, full_path,
                          db_api_auth_header, db_api_arg_header):
        r = HttpResponse()

        # Dropbox API 'download' headers
        r['Authorization'] = db_api_auth_header
        r['Dropbox-API-Arg'] = db_api_arg_header
        # Other useful headers
        r['Accept-Language'] = request.META.get('HTTP_ACCEPT_LANGUAGE')
        r['User-Agent'] = request.META.get('HTTP_USER_AGENT')
        r['Accept'] = request.META.get('HTTP_ACCEPT')
        r['Accept-Encoding'] = request.META.get('HTTP_ACCEPT_ENCODING')

        # Nginx redirect headers
        r['X-Forwarded-For'] = request.META.get('HTTP_X_FORWARDED_FOR')
        r['X-Accel-Redirect'] = settings.INTERNAL_REDIRECT_DIRECTORY
        # Include the full path so that a custom LUA block can be used
        # to sense the MIME type. NGINX can only sense based on the request
        # uri (which is general purpose in Dropbox API v2)
        r['Original-URI'] = full_path

        return r
