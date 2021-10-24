from django.urls import path

from booklist.views import (
    MainBookListView, BookListViewSet, BookListUpdateView, BookListAddBookView
)

app_name = 'booklist'

urlpatterns = [
    path('books/', BookListViewSet.as_view({'get': 'list', 'post': 'create'}), name='book-list'),
    path('books/<slug:slug>/', BookListUpdateView.as_view(), name='book-detail'),
    path('books/<slug:slug>/add-book/', BookListAddBookView.as_view(), name='booklist-add-book'),
    path('main/', MainBookListView.as_view(), name='main-booklist'),
]
