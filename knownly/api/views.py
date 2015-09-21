import logging

from django.contrib.auth import logout
from django.http import Http404
from rest_framework import response
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from . import serializers

logger = logging.getLogger(__name__)


class LogoutView(APIView):
    permission_classes = (AllowAny, )
    authentication_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        logout(request)
        return response.Response(status=201)


class UserView(RetrieveAPIView):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            raise Http404
