from rest_framework import generics
from rest_framework.response import Response

from core.models import About
from info.serializers import AboutSerializer

# About page
class AboutView(generics.RetrieveAPIView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        about = About.objects.first()
        serializer = AboutSerializer(about)
        return Response(serializer.data)
