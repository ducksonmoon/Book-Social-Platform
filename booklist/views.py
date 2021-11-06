from django.db.models import query
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import filters

from book.paginations import SmallPagesPagination
from booklist.permissions import IsOwnerOrReadOnly
from core.models import Book, BookList
from booklist.serializers import BookListSerializer, BookListAddBookSerializer
from book.serializers import BookSerializer

class BookListViewSet(viewsets.ModelViewSet):
    queryset = BookList.objects.all()
    pagination_class = SmallPagesPagination
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
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated)
    authentication_classes = (TokenAuthentication,)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, slug=self.kwargs['slug'])
        return obj


# Add specific book to a list
class BookListAddBookView(APIView):
    """ Add a book to a list """
    serializer_class = BookListAddBookSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (TokenAuthentication,)
    queryset = Book.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return Book.objects.filter(booklist=self.kwargs['book_list_id'])

    def get(self, request, slug, format=None):
        # Search book
        query = request.GET.get('search')
        if query:
            books = Book.objects.filter(title__icontains=query)
            return Response(BookSerializer(books, many=True).data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'درخواست نامعتبر است'})

    def post(self, request, slug, format=None):
        book_list = get_object_or_404(BookList, slug=slug)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data.get('book_id'))
            book = get_object_or_404(Book, pk=serializer.validated_data['book_id'])
            book_list.books.add(book)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class MainBookListView(generics.RetrieveAPIView):
    """
    صفحه مرجع 
    با عوض شدن لیست مین تفییر می‌کند.
    """
    queryset = BookList.objects.all()
    serializer_class = BookListSerializer

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj = queryset.get(slug='main')
        except BookList.DoesNotExist:
            obj = None
        return obj


class AllBookListView(generics.ListAPIView):
    """
    صفحه لیست کتاب های اضافه شده
    """
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        # Get book_set for selected book list
        q = BookList.objects.all()
        obj = get_object_or_404(q, slug=self.kwargs['slug'])
        books = obj.books.all()
        return books
