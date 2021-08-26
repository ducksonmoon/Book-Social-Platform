from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics, authentication, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User

from core.models import UserProfile
from user.serializers import (
    AuthTokenSerializer, UserSerializer, ManageUserSerializer, ChangePasswordSerializer, ConfirmCodeSerializer
)


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


class ChangePasswordView(generics.UpdateAPIView):
        """
        An endpoint for changing password.
        """
        serializer_class = ChangePasswordSerializer
        authentication_classes = (authentication.TokenAuthentication, SessionAuthentication, BasicAuthentication)
        permission_classes = (permissions.IsAuthenticated,)
        model = User

        def get_object(self, queryset=None):
            obj = self.request.user
            return obj

        def update(self, request, *args, **kwargs):
            self.object = self.get_object()
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                # Check old password
                if not self.object.check_password(serializer.data.get("old_password")):
                    return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
                # set_password also hashes the password that the user will get
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully.',
                    'data': []
                }

                return Response(response)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmCodeView(generics.CreateAPIView):
    """
    An endpoint for confirming email.
    """
    serializer_class = ConfirmCodeSerializer
    authentication_classes = (authentication.TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object = self.get_object()
            if self.object.check_confirm_code(serializer.data.get("code")):
                self.object.is_active = True
                self.object.save()
                return Response({'status': 'success', 'code': status.HTTP_200_OK, 'message': 'Email confirmed successfully.'})
            else:
                return Response({'status': 'fail', 'code': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid code.'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)