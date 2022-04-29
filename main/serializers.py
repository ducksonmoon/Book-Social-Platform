from rest_framework import serializers
from django.conf import settings
from django.urls import reverse

from core.models import CategoryPosts, Publisher


class CategoryPostsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
        base_url = settings.BASE_URL
        try: return base_url + obj.image.url
        except: return None

    link = serializers.SerializerMethodField()
    def get_link(self, obj):
        url = reverse('book:category_books', kwargs={'name': obj.name})
        base = settings.BASE_URL
        return base + url

    class Meta:
        model = CategoryPosts
        fields = ('link', 'image', 'name', 'is_active')


class PublisherSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    def get_logo(self, obj):
        base_url = settings.BASE_URL
        try: return base_url + obj.logo.url
        except: return None

    link = serializers.SerializerMethodField()
    def get_link(self, obj):
        url = reverse('book:publisher_books', kwargs={'name': obj.name})
        base = settings.BASE_URL
        return base + url

    class Meta:
        model = Publisher
        fields = ('link', 'image', 'name', 'is_active')
