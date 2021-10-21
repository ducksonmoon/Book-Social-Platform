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


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        # books is manytomany field
        books = validated_data.get('books', instance.books)
        instance.books.set(books)

        instance.save()
        return instance
    
    def validate(self, data):
        # Validate that name is not empty
        if data['name'] == '':
            raise serializers.ValidationError('Title is required')
        return data


class BookListAddBookSerializer(serializers.Serializer):
    """Serializer for adding books to a BookList"""
    book_id = serializers.IntegerField()

    def create(self, validated_data):
        """find book by book_id"""
        book_id = validated_data.get('book_id')
        book = Book.objects.get(id=book_id)
        return book

    def validate(self, data):
        """Validates that a book with the given slug exists"""
        try:
            book = Book.objects.get(id=data.get('book_id'))
        except Book.DoesNotExist:
            raise serializers.ValidationError('این کتاب وجود ندارد')
        return data