from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status, viewsets
from django.utils.translation import gettext as _
from django.contrib.auth.models import User

from core.models import UserProfile, BookList
from book.serializers import MinBookSerializer
from book.paginations import SmallPagesPagination
from booklist.serializers import BookListSerializer
from accounts.serializers import ProfileSerializer, MiniProfileSerializer
from utils.functions import report


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
            serializer = self.serializer_class(profile, context={'request': self.request})
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
            elif request.data['action'] == 'report':
                report(owner=request.user, profile=profile)
                return Response(status=status.HTTP_200_OK, data={'message': 'گزارش شما فرستاده شد'})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'User {} does not exist'.format(username)})


class ProfileBookListView(APIView):
    serializer_class = MinBookSerializer
    pagination_class = SmallPagesPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self, username, list):
        try:
            user = User.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)
            kind_list = ['liked_books', 'readed_books', 'favorite_books', 'read_later_books', 'rated_books',]
            list_choice = {
                'liked': 'liked_books',
                'reads': 'readed_books',
                'favorites': 'favorite_books',
                'read-later': 'read_later_books',
            }
            if list in list_choice.keys():
                getter = getattr(profile, list_choice[list])
                return getter.all()
            return None
        except User.DoesNotExist:
            return None

    def get(self, request, username=None, list='reads'):
        if username is None:
            username = request.user.username
        books = self.get_queryset(username, list)

        if books:
            paginator = self.pagination_class()
            serializer = self.serializer_class(books, many=True)
            page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(serializer.data)
        else:
            msg = "هیچ کتابی پیدا نشد"
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': msg})


class BookListViewSet(viewsets.ModelViewSet):
    queryset = BookList.objects.all()
    pagination_class = SmallPagesPagination
    serializer_class = BookListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        try:
            # get username slug from url
            username = self.kwargs['username']
            user = User.objects.get(username=username)
            qs = [x for x in BookList.objects.filter(user=user) if x.books.count() > 0]
            return qs
        except User.DoesNotExist:
            return None


class ProfileFollowingsView(viewsets.ModelViewSet):
    serializer_class = MiniProfileSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = SmallPagesPagination
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        try:
            username = self.kwargs['username']
            user = User.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)
            followings = profile.following.all()
            return followings
        except:
            return None
    
