from rest_framework import viewsets, mixins, status, views, generics, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from book import permissions as book_permissions
from book import serializers
from core.models import Book, UserProfile, Readers, Review
from book.serializers import BookSerializer, ReviewSerializer, ReviewDetailSerializer


class BookViewSet(APIView):
    """
    API endpoint that show book instance.
    """
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, slug):
        """
        Return a book instance.
        """
        book = get_object_or_404(Book, slug=slug)
        serializer = BookSerializer(book)
        return Response(serializer.data)


class BookActions(APIView):

    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    
    def post(self, request, slug, action):
        """
        Post request for like, dislike, and favorite, add to reading list.
        """
        book = get_object_or_404(Book, slug=slug)
        user = request.user
        if action == 'read':
            user.userprofile.read_book(book)
            return Response(status=status.HTTP_200_OK)
        elif action == 'unread':
            user.userprofile.unread_book(book)
            return Response(status=status.HTTP_200_OK)
        elif action == 'favorite':
            if user.userprofile.favorite_books.count() == 3:
                raise ValidationError(_('You can only have up to 3 favorite books.'))

            user.userprofile.add_favorite_book(book)
            return Response(status=status.HTTP_200_OK)
        elif action == 'unfavorite':
            user.userprofile.remove_favorite_book(book)
            return Response(status=status.HTTP_200_OK)
        elif action == 'add_read_later_book':
            user.userprofile.add_read_later_book(book)
            return Response(status=status.HTTP_200_OK)
        elif action == 'remove_read_later_book':
            user.userprofile.remove_read_later_book(book)
            return Response(status=status.HTTP_200_OK)
        elif action == 'rate_book':
            rate = float(request.data['rate'])
            if not 0<=rate<=5:
                raise ValidationError(_('Rate must be between 0 and 5'))
            user.userprofile.rate_book(book, rate)

            return Response(status=status.HTTP_200_OK)
        elif action == 'like_book':
            user.userprofile.like_book(book)
            return Response(status=status.HTTP_200_OK)
        elif action == 'unlike_book':
            user.userprofile.unlike_book(book)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class BookReviewViewSet(generics.ListAPIView):
    """
    API endpoint that list all reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    queryset = Review.objects.all()

    def get(self, request, slug):
        # Return all reviews for a book
        book = get_object_or_404(Book, slug=slug)
        reviews = Review.objects.filter(book=book)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        # Sumbit a new review.
        book = get_object_or_404(Book, slug=slug)
        user = request.user
        if 'text' in request.data:
            text = request.data['text']
            if not text:
                raise ValidationError(_('Review cannot be empty.'))

            user.userprofile.add_review(book, text)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailViewSet(APIView):
    """
    Review endpoint for each comment.
    Owner can change or delete a comment.
    """
    serializer_class = ReviewDetailSerializer
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, slug, pk):
        # Return a specific comment
        review = get_object_or_404(Review, pk=pk)
        serializer = ReviewDetailSerializer(review)
        return Response(serializer.data)

    def put(self, request, slug, pk):
        # Update a comment
        review = get_object_or_404(Review, pk=pk)
        if review.user != request.user:
            raise ValidationError(_('You can only edit your own comment'))
        serializer = ReviewDetailSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, pk):
        # Delete a comment
        review = get_object_or_404(Review, pk=pk)
        if review.user != request.user:
            raise ValidationError(_('You can only delete your own comment'))
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
