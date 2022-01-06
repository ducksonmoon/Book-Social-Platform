from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework import generics, authentication, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from core.models import Invitation, UserProfile, ConfirmCode
from user.serializers import (
    AuthTokenSerializer, UserSerializer, ManageUserSerializer, 
    ChangePasswordSerializer, ConfirmCodeSerializer, InvitationSerializer,
    InvitationCodeSerializer
)
from utils.validators import errors_persian_translator


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer

    # change error messages
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors = []
            for key, value in serializer.errors.items():
                msg = str(value[0])
                msg = errors_persian_translator(msg)
                errors.append(msg)
            msg = {'error': '\n'.join(errors)}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
            serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)

                return Response({'token': token.key,})
            else:
                error = serializer.errors.get('non_field_errors')[0]
                msg = {'error': error}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)


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

    def put(self, request, *args, **kwargs):
        # pass self request user to serializer
        serializer = self.serializer_class(
            instance=self.get_object(), data=request.data, partial=True,
            context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            errors = []
            for key, value in serializer.errors.items():
                msg = str(value[0])
                errors.append(msg)
            msg = {'error': '\n'.join(errors)}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

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
                    return Response({"error": "پسورد اشتباه است."}, status=status.HTTP_400_BAD_REQUEST)
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
            else:
                errors = []
                for key, value in serializer.errors.items():
                    msg = str(value[0])
                    msg = errors_persian_translator(msg)
                    errors.append(msg)
                msg = {'error': '\n'.join(errors)}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'invitations': serializer.data}, status=status.HTTP_200_OK)


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
        if request.user.userprofile.is_invited:
            return Response({'code': status.HTTP_400_BAD_REQUEST, 'error': 'اکانت فعال است'})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        try:
            invitation = Invitation.objects.get(code=code)
        except Invitation.DoesNotExist:
            return Response({'message': 'کد دعوت نا معتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        if not invitation.is_active:
            return Response({'message': 'کد دعوت استفاده شده است'}, status=status.HTTP_400_BAD_REQUEST)
        invitation.is_active = False
        invitation.receiver = request.user
        request.user.userprofile.is_invited = True
        request.user.userprofile.save()
        invitation.save()

        # Create 3 invitation codes for user.
        for _ in range(3):
            Invitation.objects.create(sender=request.user)

        return Response({'message': 'کد دعوت تایید شد'}, status=status.HTTP_200_OK)
