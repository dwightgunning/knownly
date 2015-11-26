import logging

from django.contrib.auth import logout
from rest_framework import response
from rest_framework.views import APIView

from knownly.api import serializers

logger = logging.getLogger(__name__)


class LogoutView(APIView):
    serializer_class = serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        logout(request)
        return response.Response(status=201)
