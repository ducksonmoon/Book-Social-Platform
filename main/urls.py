from django.urls import path
from . import views


urlpatterns = [
    path('', views.CategoryPostsViewSet.as_view({'get': 'list'}), name='category-posts'),
]