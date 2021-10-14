from django.urls import path

from booklist.views import BookListViewSet, BookListUpdateView


urlpatterns = [
    path('books/', BookListViewSet.as_view({'get': 'list', 'post': 'create'}), name='book-list'),
    path('books/<slug:slug>/', BookListUpdateView.as_view(), name='book-detail'),
]
