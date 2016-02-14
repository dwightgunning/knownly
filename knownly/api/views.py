import logging

from django.contrib.auth import logout
from rest_framework import response, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from knownly.api import serializers, services
from knownly.api.serializers import DirectorySerializer
from knownly.console.models import DropboxSite

logger = logging.getLogger(__name__)


class LogoutView(APIView):
    serializer_class = serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        logout(request)
        return response.Response(status=201)


class DirectoryListingView(APIView):
    authentication_classes = ()
    permission_classes = ()
    renderer_classes = (JSONRenderer, )

    def get(self, request, *args, **kwargs):
        path = kwargs["path"].lower().rstrip('/')
        domain = path.split('/')[0]
        if path.startswith(domain):
            directory = path[len(domain):]
        else:
            directory = '/'

        try:
            site = DropboxSite.objects.get(domain=domain)
        except DropboxSite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if 'directory-listings' not in site.config or \
                directory not in site.config['directory-listings']:
            return Response(status=status.HTTP_404_NOT_FOUND)

        service = services.DropboxDirectoryListingService(site.dropbox_user)
        try:
            files = service.get_directory_listing(path)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        for f in files:
            if f.path_lower.startswith(domain):
                f.path_lower = f.path_lower[len(domain):]

        serializer = DirectorySerializer(files, many=True)

        headers = {'Access-Control-Allow-Origin': '*'}

        return response.Response(serializer.data, headers=headers)
