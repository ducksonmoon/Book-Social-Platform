from django.test import TestCase, client
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import (
    UserProfile, Book, Author, Translator, Publisher, Readers,
    PersonRate,
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

    def test_friens_rate(self):
        """Test friends rating to book in book detail page"""
        url = reverse('book:book_detail', kwargs={'slug': self.book.slug})
        # autheticate me as user
        self.client.force_authenticate(user=User.objects.create_user(
            username='test',
        ))
        self.user = User.objects.get(username='test')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.user_profile.save()

        friend_user = User.objects.create(username='friend')
        friend_profile = UserProfile.objects.create(user=friend_user)
        friend_profile.rate_book(self.book, 5)
        friend_profile.save()

        self.user_profile.follow(friend_profile)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['three_friends'][0]['rate'], 5)
        
        friend_profile.rate_book(self.book, 4)
        response = self.client.get(url)
        self.assertEqual(response.data['three_friends'][0]['rate'], 4)
