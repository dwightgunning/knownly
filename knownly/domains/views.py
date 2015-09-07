import mimetypes
import urllib2

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import TemplateView


def proxy_to_mashape(request, path, target_url):
    url = '%s%s' % (target_url, path)
    if 'QUERY_STRING' in request.META:
        url += '?' + request.META['QUERY_STRING']
        url = url.replace('mashape-key=mashape-key',
                          'mashape-key=%s' % settings.MASHAPE_API_KEY)
    try:
        proxied_request = urllib2.urlopen(url)
        status_code = proxied_request.code
        mimetype = proxied_request.headers.typeheader \
            or mimetypes.guess_type(url)
        content = proxied_request.read()
    except urllib2.HTTPError as e:
        return HttpResponse(e.msg, status=e.code, content_type='text/plain')
    else:
        return HttpResponse(content, status=status_code, content_type=mimetype)


class DomainsView(TemplateView):
    template_name = 'domains/index.html'
