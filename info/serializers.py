from rest_framework import serializers
from django.conf import settings

from core.models import About


class AboutSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
        base_url = settings.BASE_URL
        try:
            return base_url + obj.image.url
        except:
            return None

    class Meta:
        model = About
        fields = ('title', 'description', 'image',)
