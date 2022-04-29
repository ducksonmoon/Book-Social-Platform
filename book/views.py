from turtle import title
import jdatetime

from rest_framework import viewsets, mixins, status, views, generics, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import filters

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from book.paginations import SmallPagesPagination
from book import permissions as book_permissions
from book import serializers
from core.models import *
from book.serializers import BookSerializer, ReviewSerializer, ReviewDetailSerializer, MinBookSerializer
from accounts.serializers import ProfileSerializer, UserForBookSerializer
from utils.functions import report

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
        serializer = BookSerializer(book, context={'request': self.request})
        return Response(serializer.data)

    def post(self, request, slug):
        """
        Post request for like, dislike, and favorite, add to reading list.
        """
        action = request.POST.get("action")
        book = get_object_or_404(Book, slug=slug)
        user = request.user

        if action == 'read':
            user.userprofile.read_book(book)
            print(user.userprofile.readed_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "به لیست اضافه شد"})

        elif action == 'unread':
            user.userprofile.unread_book(book)
            print(user.userprofile.readed_books.all())
            return Response(status=status.HTTP_200_OK , data={"message": "از لیست حذف شد"})

        elif action == 'report':
            ReportBook.objects.create(book=book, owner=user)
            return Response(status=status.HTTP_200_OK, data={"message": "گزارش شد"})

        elif action == 'favorite':
            if user.userprofile.favorite_books.count() == 3:
                raise ValidationError(_('You can only have up to 3 favorite books.'))
            user.userprofile.add_favorite_book(book)
            print(user.userprofile.favorite_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "به لیست اضافه شد"})

        elif action == 'unfavorite':
            user.userprofile.remove_favorite_book(book)
            print(user.userprofile.favorite_books.all())
            return Response(status=status.HTTP_200_OK , data={"message": "از لیست حذف شد"})

        elif action == 'add_read_later_book':
            user.userprofile.add_read_later_book(book)
            print(user.userprofile.read_later_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "به لیست اضافه شد"})

        elif action == 'remove_read_later_book':
            user.userprofile.remove_read_later_book(book)
            print(user.userprofile.read_later_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "از لیست حذف شد"})

        elif action == 'rate_book':
            rate = float(request.data['rate'])
            if not 0<=rate<=5:
                # return validation error in a dict format
                error_dict = {
                    'error': _('Rate must be between 0 and 5')
                }
                raise ValidationError(error_dict)
            user.userprofile.rate_book(book, rate)
            print(user.userprofile.rated_books.all())
            print(rate)
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})

        elif action == 'like_book':
            user.userprofile.like_book(book)
            print(user.userprofile.liked_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})

        elif action == 'unlike_book':
            user.userprofile.unlike_book(book)
            print(user.userprofile.liked_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})
        
        elif action == 'change_date':
            date = request.data['date']
            date_splited = date.split('-')
            # Jalali to Gregorian
            jdate = jdatetime.date(
                int(date_splited[0]), int(date_splited[1]), int(date_splited[2])
            )
            gdate = jdate.togregorian()
            user.userprofile.change_date_of_reading_book(book, gdate)
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})

        elif action == 'main':
            for req in request.data:
                if req == 'read':
                    user.userprofile.read_book(book)
                elif req == 'unread':
                    user.userprofile.unread_book(book)
                elif req == 'favorite':
                    if user.userprofile.favorite_books.count() == 3:
                        raise ValidationError(_('You can only have up to 3 favorite books.'))
                    user.userprofile.add_favorite_book(book)
                elif req == 'unfavorite':
                    user.userprofile.remove_favorite_book(book)
                elif req == 'add_read_later_book':
                    user.userprofile.add_read_later_book(book)
                elif req == 'remove_read_later_book':
                    user.userprofile.remove_read_later_book(book)
                elif req == 'rate_book':
                    rate = float(request.data['rate'])
                    if not 0<=rate<=5:
                        # return validation error in a dict format
                        error_dict = {
                            'error': _('Rate must be between 0 and 5')
                        }
                        raise ValidationError(error_dict)
                    user.userprofile.rate_book(book, rate)
                elif req == 'like_book':
                    user.userprofile.like_book(book)
                elif req == 'unlike_book':
                    user.userprofile.unlike_book(book)
                elif req == 'change_date':
                    date = request.data['date']
                    date_splited = date.split('-')
                    # Jalali to Gregorian
                    jdate = jdatetime.date(
                        int(date_splited[0]), int(date_splited[1]), int(date_splited[2]), locale='fa_IR'
                    )
                    gdate = jdate.togregorian()
                    user.userprofile.change_date_of_reading_book(book, gdate)

            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid action'})


class BookReviewViewSet(generics.ListAPIView):
    """
    API endpoint that list all reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    # TODO: is_invited -> Check if user is invited with invitaion code
    # for further development in future remove this filter
    queryset = Review.objects.all().filter(user__userprofile__is_invited=True)
    pagination_class = SmallPagesPagination
    ALLOWED_METHODS = ('GET', 'POST')

    def get(self, request, slug):
        # Return all reviews for a book
        book = get_object_or_404(Book, slug=slug)
        reviews = Review.objects.filter(book=book)
        serializer = ReviewSerializer(reviews, many=True)
        # paginate
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def post(self, request, slug):
        # Sumbit a new review.
        book = get_object_or_404(Book, slug=slug)
        user = request.user
        if 'text' in request.data:
            text = request.data['text']
            if not text:
                error_dict = {
                    'error': _('این فیلد نمی‌تواند خالی باشد')
                }
                raise ValidationError(error_dict)

            user.userprofile.add_review(book, text)
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid action'})


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

    def post(self, request, slug, pk):
        action = request.POST.get("action")
        if action == 'report':
            review = get_object_or_404(Review, pk=pk)
            user = request.user
            report(owner=user, review=review)
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid action'})

    def put(self, request, slug, pk):
        # Update a comment
        review = get_object_or_404(Review, pk=pk)
        if review.user != request.user:
            error_dict = {
                'error': _('You can only edit your own reviews')
            }
            raise ValidationError(error_dict)
        serializer = ReviewDetailSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid action'})

    def delete(self, request, slug, pk):
        # Delete a comment
        review = get_object_or_404(Review, pk=pk)
        if review.user != request.user:
            error_dict = {
                'error': _('You can only delete your own comment')
            }
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'درخواست نامعتبر'})
        review.delete()
        return Response(status=status.HTTP_200_OK, data={'message': 'دیدگاه حذف شد'})


class SearchViewSet(generics.ListAPIView):
    """
    API endpoint that list Search results.
    """
    queryset = Book.objects.all()
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    Method_Allowed = ['GET']

    def get(self, request):
        # Return all books
        query = request.GET.get('search')
        if query:
            # books = Book.objects.filter(title__icontains=query)[:10]
            books = Book.objects.filter(Q(title__icontains=query) | Q(title__startswith=query))
            serializer = MinBookSerializer(books, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'درخواست نامعتبر است'})


class AdvSearchViewSet(generics.ListAPIView):
    """
    API endpoint that list Search results.
    """
    queryset = Book.objects.all()
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    Method_Allowed = ['GET']

    def get(self, request):
        # Return all books
        query = request.GET.get('search')
        if query:
            # books = Book.objects.filter(title__icontains=query)[:10]
            books = Book.objects.filter(Q(title__icontains=query) | Q(title__startswith=query))
            serializer = MinBookSerializer(books, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'درخواست نامعتبر است'})


class ReadersOfBook(generics.ListAPIView):
    """
    API endpoint that list readers of a book.
    """
    serializer_class = UserForBookSerializer
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all()
    pagination_class = SmallPagesPagination
    ALLOWED_METHODS = ('GET',)

    def get(self, request, slug):
        # Return all readers of a book
        book = get_object_or_404(Book, slug=slug)
        readers = book.user_readers.all()
        serializer = UserForBookSerializer(readers, many=True, context={'book': book})
        # paginate
        page = self.paginate_queryset(readers)
        if page is not None:
            serializer = UserForBookSerializer(page, many=True, context={'book': book})
            return self.get_paginated_response(serializer.data)


class PublisherBooks(generics.ListAPIView):
    """
    API endpoint that list books of a publisher.
    """
    serializer_class = BookSerializer
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    queryset = Book.objects.all()
    pagination_class = SmallPagesPagination
    ALLOWED_METHODS = ('GET',)

    def get(self, request, name):
        # Return all readers of a book
        publisher = get_object_or_404(Publisher, name=name)
        books = Book.objects.filter(publisher=publisher)
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = BookSerializer(page, many=True,)
            return self.get_paginated_response(serializer.data)
