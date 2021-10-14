from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from booklist.permissions import IsOwnerOrReadOnly
from core.models import Book, BookList
from booklist.serializers import BookListSerializer

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
