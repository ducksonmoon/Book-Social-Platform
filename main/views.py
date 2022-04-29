from core.models import CategoryPosts, Publisher
from .serializers import *

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination


class CategoryPostsViewSet(viewsets.ModelViewSet):
    queryset = CategoryPosts.objects.all()
    serializer_class = CategoryPostsSerializer
    http_method_names = ['get']


class PublicationPostsViewSet(viewsets.ModelViewSet):
    class PagesPagination(PageNumberPagination):  
        page_size = 7
        page_size_query_param = 'page_size'

    pagination_class = PagesPagination
    queryset = Publisher.objects.filter(is_show=True)
    serializer_class = PublisherSerializer
    http_method_names = ['get']
