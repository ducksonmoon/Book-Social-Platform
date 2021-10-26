from django.template.defaultfilters import last
from rest_framework import serializers

from core.models import UserProfile, BookList
from book.serializers import BookSerializer
from booklist.serializers import BookListSerializer
class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model
    """
    username = serializers.CharField(source='user.username')
    number_of_favorits = serializers.SerializerMethodField()
    def get_number_of_favorits(self, obj):
        return obj.favorite_books.count()
    
    number_of_likes = serializers.SerializerMethodField()
    def get_number_of_likes(self, obj):
        return obj.liked_books.count()
    
    number_of_reads = serializers.SerializerMethodField()
    def get_number_of_reads(self, obj):
        return obj.readed_books.count()

    number_of_followings = serializers.SerializerMethodField()
    def get_number_of_followings(self, obj):
        return obj.following.count()
    
    number_of_read_later_books = serializers.SerializerMethodField()
    def get_number_of_read_later_books(self, obj):
        return obj.read_later_books.count()

    last_books_readed = serializers.SerializerMethodField()
    def get_last_books_readed(self, obj):
        books = obj.readed_books.all()[:3]
        return BookSerializer(books, many=True).data

    
    last_books_liked = serializers.SerializerMethodField()
    def get_last_books_liked(self, obj):
        books = obj.liked_books.all()[:3]
        return BookSerializer(books, many=True).data
    
    favorit_books = serializers.SerializerMethodField()
    def get_favorit_books(self, obj):
        books = obj.favorite_books.all()
        return BookSerializer(books, many=True).data

    last_created_lists = serializers.SerializerMethodField()
    def get_last_created_lists(self, obj):
        created_lists = BookList.objects.filter(user=obj.user)[:3]
        return BookListSerializer(created_lists, many=True).data

    last_read_later_books = serializers.SerializerMethodField()
    def get_last_read_later_books(self, obj):
        books = obj.read_later_books.all()[:3]
        return BookSerializer(books, many=True).data


    class Meta:
        model = UserProfile
        fields = (
            'id', 'username', 'name', 'birth_date', 'avatar', 'social_media_link',
            'number_of_favorits', 'number_of_likes', 'number_of_reads', 'number_of_followings', 'number_of_read_later_books',
            'last_books_readed', 'last_books_liked', 'favorit_books', 'last_created_lists', 'last_read_later_books'
        )
        read_only_fields = ('id', 'username',)
