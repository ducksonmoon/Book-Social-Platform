from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from booklist.permissions import IsOwnerOrReadOnly
from core.models import Book, BookList
from booklist.serializers import BookListSerializer, BookListAddBookSerializer
from book.serializers import BookSerializer
class BookListViewSet(viewsets.ModelViewSet):
    queryset = BookList.objects.all()
    serializer_class = BookListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return BookList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookListUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BookList.objects.all()
    serializer_class = BookListSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, slug=self.kwargs['slug'])
        return obj


# Add specif book to a list
class BookListAddBookView(APIView):
    """ Add a book to a list """
    serializer_class = BookListAddBookSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, slug):
        book_list = get_object_or_404(BookList, slug=slug)
        serializer = BookListAddBookSerializer(data=request.data)
        if serializer.is_valid():
            book = get_object_or_404(Book, id=serializer.data['book_id'])
            if book not in book_list.books.all():
                book_list.books.add(book)
                return Response(BookListSerializer(book_list).data)
            else:
                return Response({'error': 'این کتاب در لیست وجود دارد'})
        else:
            return Response({'error': 'اطلاعات ارسالی نامعتبر است'})
