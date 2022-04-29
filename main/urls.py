from django.urls import path
from . import views


urlpatterns = [
    path('posts/', views.CategoryPostsViewSet.as_view({'get': 'list'}), name='category-posts'),
    path('publishers/', views.PublicationPostsViewSet.as_view({'get': 'list'}), name='publishers'),
]