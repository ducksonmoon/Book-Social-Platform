from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from core.models import *
from book.serializers import MinBookSerializer
from .serializers import *


class CategoryPostsViewSet(viewsets.ModelViewSet):
    class PagesPagination(PageNumberPagination):  
        page_size = 7
        page_size_query_param = 'page_size'

    pagination_class = PagesPagination
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


class MainBookListViewSet(viewsets.ModelViewSet):
    class PagesPagination(PageNumberPagination):  
        page_size = 15
        page_size_query_param = 'page_size'

    pagination_class = PagesPagination
    try: queryset = BookList.objects.get(name='main').books.all()
    except: queryset = BookList.objects.none()
    serializer_class = MinBookSerializer
    http_method_names = ['get']


class BannersViewSet(viewsets.ModelViewSet):
    queryset = Baners.objects.all()
    serializer_class = BannersSerailzer
    http_method_names = ['get']
