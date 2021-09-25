from django.test import TestCase
from core.models import Book, Author, Publisher, Translator, User, UserProfile, Readers

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
        self.assertEqual(self.book.slug, 'harry-potter')

    def test_book_str(self):
        """Test __str__ method"""

        self.assertIn(self.book.title, str(self.book))

    def test_read_and_unread_book(self):
        """Read and unread books."""

        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        user.userprofile.read_book(self.book)
        self.assertEqual(user.userprofile.readed_books.first(), self.book)
        self.assertCountEqual(user.userprofile.readed_books.all(), [self.book])
        user.userprofile.unread_book(self.book)
        self.assertCountEqual(user.userprofile.readed_books.all(), [])

    def test_add_and_remove_favorites(self):
        """Add and remove books from favoritres."""

        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        self.assertCountEqual(userprofile.favorite_books.all(), [])
        userprofile.add_favorite_book(self.book)
        userprofile.add_favorite_book(self.book)
        self.assertCountEqual(userprofile.favorite_books.all(), [self.book])
        userprofile.remove_favorite_book(self.book)
        self.assertCountEqual(userprofile.favorite_books.all(), [])
    
    def test_add_favorites_existed(self):
        """Add existed item to favorites."""

        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile.add_favorite_book(self.book)
        self.assertCountEqual(userprofile.favorite_books.all(), [self.book])
        userprofile.add_favorite_book(self.book)
        self.assertCountEqual(userprofile.favorite_books.all(), [self.book])

    def test_remove_favorites_not_existed(self):
        """Test remove item that not exist in favorites"""
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile.remove_favorite_book(self.book)
        self.assertCountEqual(userprofile.favorite_books.all(), [])
    
    def test_add_favorites_more_than_three(self):
        """Add more than 3 books to favorites."""
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        for i in range(4):
            book = Book.objects.create(title='Book {}'.format(i))
            userprofile.add_favorite_book(book)
        self.assertEqual(userprofile.favorite_books.count(), 3)    
    
    def test_related_following_book(self):
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        user2 = User.objects.create(
            username='test_user2',
            password='test_password2',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile2 = UserProfile.objects.create(user=user2, name='Abbas Masomi')
        userprofile.follow(userprofile2)
        userprofile2.read_book(self.book)
        self.assertEqual(
            userprofile.related_following_to_book(self.book)[0], 
            userprofile2.user
        )
    
    def test_rate_book(self):
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile.rate_book(self.book, 5)
        self.assertEqual(userprofile.rated_books.first().book.title, self.book.title)
        self.assertEqual(userprofile.rated_books.first().person_rate, 5)
        userprofile.rate_book(self.book, 3)
        self.assertEqual(userprofile.rated_books.first().book.title, self.book.title)
        self.assertEqual(userprofile.rated_books.first().person_rate, 3)
        userprofile.rate_book(self.book, 1)
        self.assertEqual(userprofile.rated_books.first().book.title, self.book.title)
        self.assertEqual(userprofile.rated_books.first().person_rate, 1)
        userprofile.rate_book(self.book, 0)
        self.assertEqual(userprofile.rated_books.first().book.title, self.book.title)
        self.assertEqual(userprofile.rated_books.first().person_rate, 0)
        userprofile.rate_book(self.book, -1)
        self.assertEqual(userprofile.rated_books.first().book.title, self.book.title)
        self.assertEqual(userprofile.rated_books.first().person_rate, 0)
        userprofile.rate_book(self.book, 6)
        self.assertEqual(userprofile.rated_books.first().book.title, self.book.title)
        self.assertEqual(userprofile.rated_books.first().person_rate, 0)
    
    def test_rated_added_to_readed(self):
        """ Test after rate book added to readed. """
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile.read_book(self.book)
        userprofile.rate_book(self.book, 5)
        self.assertEqual(userprofile.rated_books.first().book.title, self.book.title)
        self.assertEqual(userprofile.rated_books.first().person_rate, 5)
        self.assertEqual(userprofile.readed_books.first().title, self.book.title)
    
    def test_favorite_added_to_readed(self):
        """ Test after favorite book it added to readed. """
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile.add_favorite_book(self.book)
        self.assertEqual(userprofile.favorite_books.first().title, self.book.title)
        self.assertEqual(userprofile.readed_books.first().title, self.book.title)

    def test_create_readers_obj_book_fun(self):
        """Test use read_book function for creating Readers object."""
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile.read_book(self.book)
        self.assertEqual(userprofile.readed_books.first().title, self.book.title)
        self.assertEqual(userprofile.readed_books.first(), self.book)
        self.assertEqual(Readers.objects.first().user, user)
        self.assertEqual(Readers.objects.first().book, self.book)
    
    def test_book_readers_read(self):
        """Test use book_readers function"""
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile.read_book(self.book)
        self.assertEqual(userprofile.readed_books.first(), Readers.objects.first().book)
        self.assertEqual(userprofile.readed_books.first(), self.book)
        self.assertEqual(self.book.user_readers.first(), Readers.objects.first().user)
        self.assertCountEqual(self.book.user_readers.all(), [user])
    
    def test_book_readers_unread(self):
        """Test use book_readers function"""
        user = User.objects.create(
            username='test_user',
            password='test_password',
        )
        userprofile = UserProfile.objects.create(user=user, name='Abbas Masomi')
        userprofile.read_book(self.book)
        userprofile.unread_book(self.book)
        self.assertEqual(userprofile.readed_books.first(), None)
        self.assertEqual(Readers.objects.first(), None)
        self.assertEqual(self.book.user_readers.first(), None)
        self.assertCountEqual(self.book.user_readers.all(), [])