from django.conf.urls import url
from django.urls import path

from book import views

app_name = 'book'

urlpatterns = [
    path('<slug:slug>/', views.BookViewSet.as_view(), name='book_detail'),
    path('<slug:slug>/readers/', views.ReadersOfBook.as_view(), name='readers_of_book'),
    path('<slug:slug>/reviews/', views.BookReviewViewSet.as_view(), name='reviews'),
    path('<slug:slug>/review/<int:pk>/', views.ReviewDetailViewSet.as_view(), name='review_detail'),
    path('search/title/', views.SearchViewSet.as_view(), name='search'),
    path('search/adv/', views.AdvSearchViewSet.as_view(), name='search_adv'),
    # Publishers
    path('publisher/<name>/', views.PublisherBooks.as_view(), name='publisher_books'),
]
