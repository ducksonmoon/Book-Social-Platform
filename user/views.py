from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics, authentication, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User

from core.models import Invitation, UserProfile, ConfirmCode
from user.serializers import (
    AuthTokenSerializer, UserSerializer, ManageUserSerializer, 
    ChangePasswordSerializer, ConfirmCodeSerializer, InvitationSerializer,
    InvitationCodeSerializer
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


class SendConfirmCodeView(generics.GenericAPIView):
    """Send a confirm code to the user's email with no content."""

    authentication_classes = (authentication.TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user

    def create(self, request, *args, **kwargs):
        """Create a new confirm code"""
        user = self.get_object()
        try:
            ConfirmCode.objects.get(user=user).delete()
            code = ConfirmCode.objects.create(user=user)

        except ConfirmCode.DoesNotExist:
            code = ConfirmCode.objects.create(user=user)
        code.send_confirm_code_to_email()
        return Response({"status": "success", "code": status.HTTP_200_OK, "message": "Confirm code sent."},
                        status=status.HTTP_200_OK)


class VerifyEmailView(generics.GenericAPIView):
    """
    An endpoint for verifying email.
    """
    serializer_class = ConfirmCodeSerializer
    authentication_classes = (authentication.TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = ConfirmCode.objects.get(code=self.kwargs['code'])
        return obj

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['code'] = serializer.validated_data['code']
        self.kwargs['email'] = serializer.validated_data['email']
        user = User.objects.get(email=self.kwargs['email'])
        if user.confirmcode.code == self.kwargs['code']:
            user.is_active = True
            user.save()
            return Response({'status': 'success', 'code': status.HTTP_200_OK, 'message': 'Email verified successfully.'})
        else:
            return Response({'status': 'fail', 'code': status.HTTP_400_BAD_REQUEST, 'message': 'Invalid code.'})


class InvitationView(generics.ListAPIView):
    """
    An endpoint for retrieving invitations of authenticated user.
    """
    serializer_class = InvitationSerializer
    authentication_classes = (authentication.TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        Return invitations of authenticated user.
        """
        qs = Invitation.objects.filter(
            is_active=True,
            sender=self.request.user
        )
        return qs

    def get(self, request, *args, **kwargs):
        """
        Return invitations of authenticated user.
        """
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response({'status': 'success', 'code': status.HTTP_200_OK, 'message': 'Invitations retrieved successfully.',
                         'invitations': serializer.data}, status=status.HTTP_200_OK)


# Enter invitation code to activate account
class InvitationCodeView(generics.GenericAPIView):
    """
    An endpoint for retrieving invitation code.
    """
    serializer_class = InvitationCodeSerializer
    authentication_classes = (authentication.TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Activate account with invitation code.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        try:
            invitation = Invitation.objects.get(code=code)
        except Invitation.DoesNotExist:
            return Response({'status': 'fail', 'code': status.HTTP_400_BAD_REQUEST, 'message': 'Invitation code does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not invitation.is_active:
            return Response({'status': 'fail', 'code': status.HTTP_400_BAD_REQUEST, 'message': 'Invitation code has already been used.'},
                            status=status.HTTP_400_BAD_REQUEST)
        invitation.is_active = False
        invitation.receiver = request.user
        request.user.userprofile.is_invited = True
        invitation.save()

        # Create 3 invitation codes for user.
        for _ in range(3):
            Invitation.objects.create(sender=request.user)

        return Response({'status': 'success', 'code': status.HTTP_200_OK, 'message': 'Invitation code activated successfully.'},
                        status=status.HTTP_200_OK)
