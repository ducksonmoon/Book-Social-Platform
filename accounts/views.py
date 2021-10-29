from accounts.serializers import ProfileSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from core.models import UserProfile
from django.contrib.auth.models import User


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self, username):
        try:
            user = User.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)
            return profile
        except User.DoesNotExist:
            return None
    
    def get(self, request, username=None):
        if username is None:
            username = request.user.username

        profile = self.get_object(username)
        if profile:
            serializer = self.serializer_class(profile)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


    def post(self, request, username=None):
        """ Follow and unfollow a user """

        profile = self.get_object(username)
        if profile:
            user = request.user.userprofile
            # Follow other user
            if request.data['action'] == 'follow':
                user.follow(profile)
                return Response(status=status.HTTP_200_OK, data={'message': 'You are now following {}'.format(username)})
            # Unfollow other user
            elif request.data['action'] == 'unfollow':
                user.unfollow(profile)
                return Response(status=status.HTTP_200_OK, data={'message': 'You are no longer following {}'.format(username)})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'User {} does not exist'.format(username)})
