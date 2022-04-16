from core.models import CategoryPosts
from .serializers import CategoryPostsSerializer

from rest_framework import viewsets


class CategoryPostsViewSet(viewsets.ModelViewSet):
    queryset = CategoryPosts.objects.all()
    serializer_class = CategoryPostsSerializer
    http_method_names = ['get']
    