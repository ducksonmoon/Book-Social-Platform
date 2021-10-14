from django.test import TestCase
from django.contrib.auth.models import User

from core.models import BookList, Book
class BookListModelTest(TestCase):
    """Test Book list model"""
    def test_create_book_list(self):
        # Test creating a book list
        user = User.objects.create(username='testuser', password='12345')
        book_list = BookList.objects.create(name='Test Book List', user=user)
        self.assertEqual(book_list.name, 'Test Book List')
