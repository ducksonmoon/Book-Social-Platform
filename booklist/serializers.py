from rest_framework import serializers
from core.models import BookList, Book


class BookListSerializer(serializers.ModelSerializer):
    """Serializer for BookList objects"""
    user = serializers.ReadOnlyField(source='user.username')
    books = serializers.PrimaryKeyRelatedField(many=True, queryset=Book.objects.all())
    books_title = serializers.SerializerMethodField()
    def get_books_title(self, obj):
        """Returns a list of book titles"""
        return [book.title for book in obj.books.all()]

    class Meta:
        model = BookList
        fields = '__all__'
        read_only_fields = ('id', 'user', 'date_created', 'is_active', 'slug')
