from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import (
    UserProfile, Book, Author, Translator, Publisher,
)
'''

class BookAPIPublicTest(TestCase):
    """Test Book api public."""
    
    def setUp(self) -> None:
        self.client = APIClient()

        # Create Book instance.
        self.auther = Author.objects.create(name='J.K. Rowling')
        self.publisher = Publisher.objects.create(name='Penguin')
        self.translator = Translator.objects.create(name='J.K. Rowling')
        # Authors and Translators are many to many field in book model
        self.book = Book.objects.create(title='Harry Potter')
        self.book.authors.add(self.auther)
        self.book.translators.add(self.translator)
        self.book.publisher = self.publisher
        self.book.save()

    # Test public book information.
    def test_book_api_public_get(self):
        # Get book instance.
        response = self.client.get(reverse('book', kwargs={'pk': self.book.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Harry Potter')
        self.assertEqual(response.data['authors'][0]['name'], 'J.K. Rowling')
        self.assertEqual(response.data['translators'][0]['name'], 'J.K. Rowling')
        self.assertEqual(response.data['publisher']['name'], 'Penguin')
'''