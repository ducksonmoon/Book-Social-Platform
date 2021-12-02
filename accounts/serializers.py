from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings

from core.models import UserProfile, BookList
from book.serializers import BookSerializer, MinBookSerializer
from booklist.serializers import BookListSerializer
from accounts.functions import is_following


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model
    """
    username = serializers.CharField(source='user.username')
    is_following = serializers.SerializerMethodField()
    def get_is_following(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return is_following(user, obj.user)
        else:
            return False

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
        books = obj.readed_books.all()[:2]
        return MinBookSerializer(books, many=True).data

    last_books_liked = serializers.SerializerMethodField()
    def get_last_books_liked(self, obj):
        books = obj.liked_books.all()[:2]
        return MinBookSerializer(books, many=True).data
    
    favorit_books = serializers.SerializerMethodField()
    def get_favorit_books(self, obj):
        books = obj.favorite_books.all()
        return MinBookSerializer(books, many=True).data

    last_created_lists = serializers.SerializerMethodField()
    def get_last_created_lists(self, obj):
        created_lists = BookList.objects.filter(user=obj.user)[:2]
        # remove empty lists from created_lists
        created_lists = [x for x in created_lists if x.books.count() > 0]
        return BookListSerializer(created_lists, many=True).data

    last_read_later_books = serializers.SerializerMethodField()
    def get_last_read_later_books(self, obj):
        books = obj.read_later_books.all()[:2]
        return MinBookSerializer(books, many=True).data


    class Meta:
        model = UserProfile
        fields = (
            'id', 'username', 'name', 'birth_date', 'avatar', 'social_media_link',
            'is_following', 'is_invited',
            'number_of_favorits', 'number_of_likes', 'number_of_reads', 'number_of_followings', 'number_of_read_later_books',
            'last_books_readed', 'last_books_liked', 'favorit_books', 'last_created_lists', 'last_read_later_books'
        )
        read_only_fields = ('id', 'username',)


class UserForBookSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model
    At specific book readers
    """
    name = serializers.CharField(source='userprofile.name')
    avatar = serializers.SerializerMethodField()
    def get_avatar(self, obj):
        try:
            return settings.BASE_URL + obj.userprofile.avatar.url
        except:
            return 'https://api.nebigapp.com/media/defaults/avatar.png'
    
    rate_to_book = serializers.SerializerMethodField()
    def get_rate_to_book(self, obj):
        user = obj
        book = self.context['book']
        if user.is_authenticated:
            return user.userprofile.rate_of_book(book)
        else:
            return None


    class Meta:
        model = User
        fields = (
            'id', 'username', 'name', 'avatar', 'rate_to_book',
        )
        read_only_fields = ('id', 'username',)


class MiniProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model
    """
    username = serializers.CharField()
    readed_books = serializers.SerializerMethodField()
    def get_readed_books(self, obj):
        print(obj.userprofile.readed_books.all().count())
        return obj.userprofile.readed_books.all().count()

    avatar = serializers.SerializerMethodField()
    def get_avatar(self, obj):
        try:
            return settings.BASE_URL + obj.userprofile.avatar.url
        except:
            return 'https://api.nebigapp.com/media/defaults/avatar.png'

    class Meta:
        model = UserProfile
        fields = (
            'id', 'username', 'avatar', 'readed_books',
        )
        read_only_fields = ('id', 'username',)