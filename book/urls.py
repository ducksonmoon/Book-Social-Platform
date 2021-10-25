from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'book'

urlpatterns = [
    path('<slug:slug>/', views.BookViewSet.as_view(), name='book_detail'),
    path('<slug:slug>/reviews/', views.BookReviewViewSet.as_view(), name='reviews'),
    path('<slug:slug>/review/<int:pk>/', views.ReviewDetailViewSet.as_view(), name='review_detail'),
    path('search/title/', views.SearchViewSet.as_view(), name='search'),
]
