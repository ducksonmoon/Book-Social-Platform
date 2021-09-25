from django.test import TestCase, client
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import (
    UserProfile, Book, Author, Translator, Publisher, Readers
)
from book.serializers import BookSerializer


class BookAPIPublic(TestCase):
    """Test the book API public"""

    def setUp(self):
        self.auther = Author.objects.create(name='F. Scott Fitzgerald')
        self.publisher = Publisher.objects.create(name='Penguin')
        self.translator = Translator.objects.create(name='John Doe')
        # Authors and Translators are many to many field in book model
        self.book = Book.objects.create(title='The Great Gatsby')
        self.book.authors.add(self.auther)
        self.book.translators.add(self.translator)
        self.book.publisher = self.publisher
        self.book.save()
        self.client = APIClient()

    def test_book_serializer(self):
        """Test the book serializer"""
        book_serializer = BookSerializer(self.book)
        self.assertEqual(book_serializer.data['title'], 'The Great Gatsby')
        self.assertEqual(book_serializer.data['authors'][0], 'F. Scott Fitzgerald')
        self.assertEqual(book_serializer.data['translators'][0], 'John Doe')
        self.assertEqual(book_serializer.data['publisher'], 'Penguin')
    
    def test_book_information(self):
        """Test book information."""
        BOOK_URL = reverse('book:book_detail', kwargs={'slug': self.book.slug})
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'The Great Gatsby')
        self.assertEqual(response.data['authors'][0], 'F. Scott Fitzgerald')
        self.assertEqual(response.data['translators'][0], 'John Doe')
        self.assertEqual(response.data['publisher'], 'Penguin')

    def test_book_information_not_found(self):
        """Test book information not found."""
        BOOK_URL = reverse('book:book_detail', kwargs={'slug': 'not-found'})
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, 404)

    def test_book_actions(self):
        """Test book actions."""
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'like'})
        response = self.client.post(BOOK_URL)
        self.assertEqual(response.status_code, 401)
    
    def test_book_reviews(self):
        """Test book reviews."""
        BOOK_URL = reverse('book:reviews', kwargs={'slug': self.book.slug})
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, 200)

class BookAPIPrivate(TestCase):
    """Test the book API private"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.userprofile = UserProfile.objects.create(user=self.user, name='Abbas Masomi')
        client = APIClient()
        client.force_authenticate(user=self.user)
        self.client = client
        self.auther = Author.objects.create(name='F. Scott Fitzgerald')
        self.publisher = Publisher.objects.create(name='Penguin')
        self.translator = Translator.objects.create(name='John Doe')
        # Authors and Translators are many to many field in book model
        self.book = Book.objects.create(title='The Great Gatsby')
        self.book.authors.add(self.auther)
        self.book.translators.add(self.translator)
        self.book.publisher = self.publisher
        self.book.save()

    def test_book_actions_read(self):
        """Test book actions read."""
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'read'})
        response = self.client.post(BOOK_URL)
        a = Book.user_readers.through.objects.get(user=self.user, book=self.book)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(a.user, self.user)
        self.assertEqual(a.book, self.book)
        self.assertEqual(self.book, self.userprofile.readed_books.all()[0])
        b = Readers.objects.get(user=self.user, book=self.book)
        self.assertEqual(b.user, self.user)
        self.assertEqual(b.book, self.book)
        self.assertEqual(list(self.book.user_readers.all()), [self.user])
        self.assertEqual(list(self.userprofile.readed_books.all()), [self.book])

    def test_book_actions_favorite_book(self):
        """Test favorite book."""
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'favorite'})
        response = self.client.post(BOOK_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.book, self.userprofile.favorite_books.all()[0])
        self.assertEqual(self.userprofile.favorite_books.all().count(), 1)
        self.assertCountEqual(self.userprofile.readed_books.all(), [self.book])
        self.assertEqual(list(self.userprofile.favorite_books.all()), [self.book])
    
    def test_book_actions_favorite_books_more_than3(self):
        """Test favorite books more than 3."""
        for i in range(3):
            book = Book.objects.create(title=f'The Great Gatsby{i}')
            BOOK_URL = reverse('book:actions', kwargs={'slug': book.slug, 'action': 'favorite'})
            response = self.client.post(BOOK_URL)
            self.assertEqual(response.status_code, 200)
        for i in range(2):
            book = Book.objects.create(title=f'The Great Gatsby{i+3}')
            BOOK_URL = reverse('book:actions', kwargs={'slug': book.slug, 'action': 'favorite'})
            response = self.client.post(BOOK_URL)
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.userprofile.favorite_books.all().count(), 3)
    
    def test_book_actions_unread(self):
        """Test book actions unread."""
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'unread'})
        response = self.client.post(BOOK_URL)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual([], self.userprofile.readed_books.all())
        self.assertCountEqual([], self.book.user_readers.all())
        self.assertCountEqual(Readers.objects.filter(user=self.user, book=self.book), [])
    
    def test_book_actions_unfavorite(self):
        """Test book actions unfavorite."""
        BOOK_URL_FAV = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'favorite'})
        response1 = self.client.post(BOOK_URL_FAV)
        BOOK_URL_UNFAVE = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'unfavorite'})
        response2 = self.client.post(BOOK_URL_UNFAVE)

        self.assertEqual(response2.status_code, 200)
        self.assertCountEqual([], self.userprofile.favorite_books.all())
        self.assertCountEqual([self.user], self.book.user_readers.all())
    
    def test_book_read_later(self):
        """Test book read later."""
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'add_read_later_book'})
        response = self.client.post(BOOK_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.book, self.userprofile.read_later_books.all()[0])
        self.assertEqual(self.userprofile.read_later_books.all().count(), 1)
        self.assertCountEqual(self.userprofile.readed_books.all(), [])
        self.assertEqual(list(self.userprofile.read_later_books.all()), [self.book])

    def test_book_remove_read_later(self):
        """Test book remove read later."""
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'add_read_later_book'})
        response = self.client.post(BOOK_URL)
        BOOK_URL_REMOVE = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'remove_read_later_book'})
        response2 = self.client.post(BOOK_URL_REMOVE)
        self.assertEqual(response2.status_code, 200)
        self.assertCountEqual([], self.userprofile.read_later_books.all())
        self.assertCountEqual([], self.book.user_readers.all())

    def test_book_rate(self):
        """Test book rate."""
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'rate_book'})
        response = self.client.post(BOOK_URL, {'rate': 4})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.book, self.userprofile.rated_books.all()[0].book)
        self.assertEqual(self.userprofile.rated_books.all().count(), 1)
        self.assertEqual(self.userprofile.rated_books.all()[0].person_rate, 4)
        self.assertEqual(self.userprofile.rated_books.first().book.title, self.book.title)

    def test_book_rate_float(self):
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'rate_book'})
        response = self.client.post(BOOK_URL, {'rate': 4.5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.book, self.userprofile.rated_books.all()[0].book)
        self.assertEqual(self.userprofile.rated_books.all().count(), 1)
        self.assertEqual(self.userprofile.rated_books.all()[0].person_rate, 4.5)
        self.assertEqual(self.userprofile.rated_books.first().book.title, self.book.title)

    def test_book_rate_great_or_lower_number(self):
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'rate_book'})
        response = self.client.post(BOOK_URL, {'rate': 6})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.userprofile.rated_books.all().count(), 0)

    def test_book_like(self):
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'like_book'})
        response = self.client.post(BOOK_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.book.title, self.userprofile.liked_books.all()[0].title)
        self.assertEqual(self.userprofile.liked_books.all().count(), 1)
        self.assertEqual(self.book.user_liked.all().count(), 1)
        self.assertEqual(self.book.user_liked.all()[0].username, self.user.username)

    def test_book_remove_like(self):
        BOOK_URL = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'like_book'})
        response = self.client.post(BOOK_URL)
        BOOK_URL_REMOVE = reverse('book:actions', kwargs={'slug': self.book.slug, 'action': 'unlike_book'})
        response2 = self.client.post(BOOK_URL_REMOVE)
        self.assertEqual(response2.status_code, 200)
        self.assertCountEqual([], self.userprofile.liked_books.all())
        self.assertCountEqual([], self.book.user_liked.all())

    def test_book_add_review(self):
        BOOK_REVIEW_URL = reverse('book:reviews', kwargs={'slug': self.book.slug})
        response = self.client.post(BOOK_REVIEW_URL, {'text': 'test'})
        self.assertEqual(response.status_code, 200)

        # Book
        self.assertEqual(self.book.reviews.all().count(), 1)
        self.assertEqual(self.book.reviews.all()[0].text, 'test')

        # ME
        self.assertEqual(self.userprofile.reviews.all().count(), 1)
        self.assertEqual(self.userprofile.reviews.all()[0].text, 'test')

    def test_book_add_review_empty(self):
        BOOK_REVIEW_URL = reverse('book:reviews', kwargs={'slug': self.book.slug})
        response = self.client.post(BOOK_REVIEW_URL, {'text': ''})
        self.assertEqual(response.status_code, 400)

        # Book
        self.assertEqual(self.book.reviews.all().count(), 0)

        # ME
        self.assertEqual(self.userprofile.reviews.all().count(), 0)

    def test_book_add_review_long(self):
        BOOK_REVIEW_URL = reverse('book:reviews', kwargs={'slug': self.book.slug})
        response = self.client.post(BOOK_REVIEW_URL, {'text': 'test' * 10000000})
        self.assertEqual(response.status_code, 400)

        # Book
        self.assertEqual(self.book.reviews.all().count(), 0)

        # ME
        self.assertEqual(self.userprofile.reviews.all().count(), 0)
    
    def test_book_review_detail(self):
        BOOK_REVIEW_URL = reverse('book:reviews', kwargs={'slug': self.book.slug})
        response = self.client.post(BOOK_REVIEW_URL, {'text': 'test'})
        pk = self.book.reviews.all()[0].pk
        BOOK_REVIEW_DETAIL_URL = reverse('book:review_detail', kwargs={'slug': self.book.slug, 'pk': pk})
        response = self.client.get(BOOK_REVIEW_DETAIL_URL)
        self.assertEqual(response.status_code, 200)

    def test_book_review_remove(self):
        BOOK_REVIEW_URL = reverse('book:reviews', kwargs={'slug': self.book.slug})
        response = self.client.post(BOOK_REVIEW_URL, {'text': 'test'})
        pk = self.book.reviews.all()[0].pk
        BOOK_REVIEW_DETAIL_URL = reverse('book:review_detail', kwargs={'slug': self.book.slug, 'pk': pk})
        response = self.client.delete(BOOK_REVIEW_DETAIL_URL)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.book.reviews.all().count(), 0)
        self.assertEqual(self.userprofile.reviews.all().count(), 0)

    def test_change_review(self):
        BOOK_REVIEW_URL = reverse('book:reviews', kwargs={'slug': self.book.slug})
        response = self.client.post(BOOK_REVIEW_URL, {'text': 'test'})
        pk = self.book.reviews.all()[0].pk
        BOOK_REVIEW_DETAIL_URL = reverse('book:review_detail', kwargs={'slug': self.book.slug, 'pk': pk})
        response = self.client.put(BOOK_REVIEW_DETAIL_URL, {'text': 'test2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.book.reviews.all()[0].text, 'test2')
        self.assertEqual(self.userprofile.reviews.all()[0].text, 'test2')
    
    def test_comments_book_information(self):
        for i in range(5):
            BOOK_REVIEW_URL = reverse('book:reviews', kwargs={'slug': self.book.slug})
            self.client.post(BOOK_REVIEW_URL, {'text': f'test{i}'})

        BOOK_URL = reverse('book:book_detail', kwargs={'slug': self.book.slug})
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, 200)

