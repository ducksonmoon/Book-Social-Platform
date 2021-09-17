from django.test import TestCase
from core.models import Book, Author, Publisher, Translator

class TestBookModel(TestCase):
    
    def setUp(self) -> None:
        self.auther = Author.objects.create(name='J.K. Rowling')
        self.publisher = Publisher.objects.create(name='Penguin')
        self.translator = Translator.objects.create(name='J.K. Rowling')
        # Authors and Translators are many to many field in book model
        self.book = Book.objects.create(title='Harry Potter')
        self.book.authors.add(self.auther)
        self.book.translators.add(self.translator)
        self.book.publisher = self.publisher
        self.book.save()

    def test_crete_book_obj(self):
        """Create a book instance"""

        self.assertIsInstance(self.book, Book)
        self.assertEqual(self.book.title, 'Harry Potter')
        self.assertEqual(self.book.publisher, self.publisher)
        self.assertEqual(self.book.authors.first(), self.auther)
        self.assertEqual(self.book.translators.first(), self.translator)
