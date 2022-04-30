from django.urls import path
from . import views


urlpatterns = [
    path('categoryPosts/', views.CategoryPostsViewSet.as_view({'get': 'list'}), name='category-posts'),
    path('publishers/', views.PublicationPostsViewSet.as_view({'get': 'list'}), name='publishers'),
    path('mainBookList/', views.MainBookListViewSet.as_view({'get': 'list'}), name='main-book-list'),
    path('banners/', views.BannersViewSet.as_view({'get': 'list'}), name='banners'),
]