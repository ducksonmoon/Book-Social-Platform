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
        read_only_fields = ('id', 'user', 'date_created', 'is_active')


class UpdateBookSerializer(serializers.Serializer):
    """Serializer for adding a book to a BookList"""
    book_id = serializers.IntegerField()
    book_list_id = serializers.IntegerField()

    def validate(self, data):
        """Check that the book and booklist exist"""
        book_id = data.get('book_id')
        book_list_id = data.get('book_list_id')
        try:
            Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError("این کتاب وجود ندارد")
        try:
            BookList.objects.get(id=book_list_id)
        except BookList.DoesNotExist:
            raise serializers.ValidationError("این لیست وجود ندارد")
        return data

    def create(self, validated_data):
        """Add book to booklist"""
        book_id = validated_data.get('book_id')
        book_list_id = validated_data.get('book_list_id')
        book = Book.objects.get(id=book_id)
        book_list = BookList.objects.get(id=book_list_id)
        book_list.books.add(book)
        return book_list
    
    def update(self, instance, validated_data):
        """Remove book from booklist"""
        book_id = validated_data.get('book_id')
        book_list_id = validated_data.get('book_list_id')
        book = Book.objects.get(id=book_id)
        book_list = BookList.objects.get(id=book_list_id)
        book_list.books.remove(book)
        return book_list

    def delete(self, instance):
        """Remove book from booklist"""
        book_list_id = instance.id
        book_list = BookList.objects.get(id=book_list_id)
        book_list.books.clear()
        return book_list

    class Meta:
        fields = ('book_id', 'book_list_id')
