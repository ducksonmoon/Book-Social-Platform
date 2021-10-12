from django.urls import path

from booklist.views import BookListViewSet


urlpatterns = [
    path('books/', BookListViewSet.as_view({'get': 'list', 'post': 'create'}), name='book-list'),
]
