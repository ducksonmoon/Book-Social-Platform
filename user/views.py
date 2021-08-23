from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics, authentication, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from core.models import UserProfile
from user.serializers import AuthTokenSerializer, UserSerializer, ManageUserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = ManageUserSerializer
    authentication_classes = (authentication.TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Return the authenticated user"""
        return UserProfile.objects.all()

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user.userprofile