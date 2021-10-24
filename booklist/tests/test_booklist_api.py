from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from core.models import BookList, Book
from django.contrib.auth.models import User

class BookListAPITestCase(TestCase):
    """Test BookList API"""
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='test1213',
            email='test@test2.com',
            password='testpass1234',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_booklist(self):
        # Create a booklist
        response = self.client.post('/list/books/', {'name': 'New BookList'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BookList.objects.count(), 1)
        self.assertEqual(BookList.objects.get().name, 'New BookList')

    def test_get_booklist(self):
        # Get a booklist
        booklist = BookList.objects.create(name='New BookList', user=self.user)
        response = self.client.get(f'/list/books/{booklist.slug}/')
        self.assertEqual(response.status_code, 200)
    
    def test_update_booklist(self):
        # Update a booklist
        booklist = BookList.objects.create(name='New BookList', user=self.user)
        response = self.client.put(f'/list/books/{booklist.slug}/', {'name': 'Updated BookList'})
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BookList.objects.get().name, 'Updated BookList')
    
    def test_delete_booklist(self):
        # Delete a booklist
        booklist = BookList.objects.create(name='New BookList', user=self.user)
        response = self.client.delete(f'/list/books/{booklist.slug}/')

        self.assertEqual(response.status_code, 204)
        self.assertEqual(BookList.objects.count(), 0)
    
    def test_create_booklist_with_invalid_name(self):
        # Create a booklist with invalid name
        response = self.client.post('/list/books/', {'name': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(BookList.objects.count(), 0)

    def test_get_main_booklist_non_exsistent(self):
        # Get main booklist
        MAIN_URL = reverse('booklist:main-booklist')
        response = self.client.get(MAIN_URL)
        self.assertEqual(response.status_code, 200)

    def test_get_main_booklist(self):
        # Get main booklist
        MAIN_URL = reverse('booklist:main-booklist')
        booklist = BookList.objects.create(name='main', user=self.user, slug='main')
        ADD_BOOK_URL = reverse('booklist:booklist-add-book', kwargs={'slug': booklist.slug})
        Book.objects.create(title='test')
        self.client.post(ADD_BOOK_URL, {'slug': 'main', 'book_id': 1})
        response = self.client.get(MAIN_URL)
        books = BookList.objects.get(slug='main').books.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(books.count(), 1)
