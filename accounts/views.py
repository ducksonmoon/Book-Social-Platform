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
