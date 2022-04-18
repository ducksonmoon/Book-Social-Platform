from pyexpat import model
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import RegexValidator

from PIL import Image
import random
import string
from io import BytesIO
import sys

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=150, blank=True)
    email = models.EmailField(max_length=150, blank=True)
    phone = models.CharField(max_length=150, blank=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='defaults/avatar-happy.png')
    SOCIAL_MEDIA_CHOICES = (
        ('twitter', 'Twitter'),   # There was 3 options but for but we only use one.
    )
    social_media_username = models.CharField(max_length=255, blank=True, choices=SOCIAL_MEDIA_CHOICES)
    social_media_link = models.CharField(max_length=255, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    # User is invited: boolean -> True or False
    is_invited = models.BooleanField(default=False)
    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following', blank=True)

    reviews = models.ManyToManyField('Review', related_name='reviews', blank=True)

    liked_books = models.ManyToManyField('Book', related_name='liked_books', blank=True)

    readed_books = models.ManyToManyField('Book', related_name='readed_books', blank=True) 

    favorite_books = models.ManyToManyField('Book', related_name='favorite_books', blank=True)

    read_later_books = models.ManyToManyField('Book', related_name='read_later_books', blank=True)

    rated_books = models.ManyToManyField('PersonRate', related_name='rated_books', blank=True)

    def add_read_later_book(self, book):
        if book not in self.read_later_books.all():
            self.read_later_books.add(book)
            return True
        return False

    def remove_read_later_book(self, book):
        if book in self.read_later_books.all():
            self.read_later_books.remove(book)
            return True
        return False

    def add_favorite_book(self, book):
        if book not in self.favorite_books.all() and self.favorite_books.count() < 3:
            self.favorite_books.add(book)
            self.read_book(book)
            return True
        return False

    def remove_favorite_book(self, book):
        if book in self.favorite_books.all():
            self.favorite_books.remove(book)
            return True
        return False

    def follow(self, user):
        if user not in self.following.all() and user.user != self.user:
            self.following.add(user.user)
            user.followers.add(self.user)
            return True
        return False

    def unfollow(self, user):
        if user.user in self.following.all() and user.user != self.user:
            self.following.remove(user.user)
            user.followers.remove(self.user)
            return True
        return False

    def read_book(self, book):
        # if books instance not in readed book add it.
        if book not in self.readed_books.all():
            self.readed_books.add(book)
            Readers.objects.create(user=self.user, book=book)
            book.user_readers.add(self.user)
            return True
        return False

    def unread_book(self, book):
        # if books instance in readed book remove it.
        if book in self.readed_books.all():
            self.readed_books.remove(book)
            Readers.objects.filter(user=self.user, book=book).delete()
            book.user_readers.remove(self.user)
            return True
        return False

    # Change date of reading book
    def change_date_of_reading_book(self, book, date):
        if book in self.readed_books.all():
            Readers.objects.filter(user=self.user, book=book).update(date_readed=date)
            return True
        return False

    def has_readed_book(self, book):
        return book in self.readed_books.all()

    def related_following_to_book(self, book):
        result = []
        for u in self.following.all():
            try:
                if book in u.userprofile.readed_books.all():
                    result.append(u)
            except:
                pass
        return result

    def rate_book(self, book, rate):
        if (book in Book.objects.all()) and 0<=rate<=5:
            self_rate = PersonRate.objects.filter(user=self.user, book=book)
            if self_rate.exists():                
                self_rate.update(person_rate=rate)
            else:
                obj = PersonRate.objects.create(user=self.user, book=book, person_rate=rate)
                self.rated_books.add(obj)
                if book not in self.readed_books.all():
                    self.read_book(book)
            return True

        return False

    def like_book(self, book):
        if book not in self.liked_books.all() and book in Book.objects.all():
            self.liked_books.add(book)
            book.user_liked.add(self.user)
            self.read_book(book)
            return True
        return False
    
    def unlike_book(self, book):
        if book in self.liked_books.all() and book in Book.objects.all():
            self.liked_books.remove(book)
            book.user_liked.remove(self.user)
            return True
        return False
    
    def add_review(self, book, review):
        if book in Book.objects.all():
            review = Review.objects.create(user=self.user, book=book, text=review)
            self.reviews.add(review)
            book.reviews.add(review)
            return True
        return False

    def remove_review(self, book, review):
        if review in self.reviews.all():
            Review.objects.filter(user=self.user, book=book, text=review).delete()
            self.reviews.remove(review)
            book.reviews.remove(review)
            return True
        return False
    
    def rate_of_book(self, book):
        if book in Book.objects.all():
            rate = PersonRate.objects.filter(user=self.user, book=book)
            if rate:
                return rate[0].person_rate
            return 0

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        # Resize the image to a square
        if self.avatar:
            # resize the image to a square 300x300 pixels
            img = Image.open(self.avatar)
            if img.height > img.width:
                diff = img.height - img.width
                img = img.crop((0, diff // 2, img.width, img.height - diff // 2))
            elif img.height < img.width:
                diff = img.width - img.height
                img = img.crop((diff // 2, 0, img.width - diff // 2, img.height))
            img.thumbnail((300, 300))
            img.save(self.avatar.path)
            """
            img = Image.open(self.avatar)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
            """
    def __str__(self):
        return self.user.username


class PersonRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    person_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.5), MaxValueValidator(5.00)],  blank=True, null=True)

    def __str__(self):
        return self.user.username + ' ' + self.book.title


class ConfirmCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(
        max_length=255, 
        unique=True,
    )
    expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def check_confirm_code(self, code):
        if self.code == code and self.expires > timezone.now():
            return True
        return False

    def generate_confirm_code(self):
        self.code = ''.join(random.choice(string.digits) for _ in range(6))
        self.expires = timezone.now() + timezone.timedelta(minutes=10)
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            # self.code must be unique
            code = self.generate_confirm_code()
            while ConfirmCode.objects.filter(code=code).exists():
                code = self.generate_confirm_code()
            self.code = code

        super(ConfirmCode, self).save(*args, **kwargs)

    def send_confirm_code_to_email(self):
        send_mail(
            'Confirm Code', 
            'Your confirm code is ' + self.code, 
            settings.EMAIL_HOST_USER, 
            [self.user.email], 
            fail_silently=False
        )


class Invitation(models.Model):
    sender = models.ForeignKey(User, related_name='invitations_sent', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='invitations_received', on_delete=models.CASCADE, null=True)
    code = models.CharField(
        max_length=255, 
        unique=True,
    )
    date_created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.receiver:
            return self.sender.username + ' invited ' + self.receiver.username
        else:
            return self.sender.username

    def generate_invitation_code(self):
        self.code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return self.code
    
    def save(self, *args, **kwargs):
        if not self.code:
            code = self.generate_invitation_code()
            # Check if code esxist create new code till it's unique
            while Invitation.objects.filter(code=code).exists():
                code = self.generate_invitation_code()
            self.code = code

        super(Invitation, self).save(*args, **kwargs)

    def check_invitation(self, code):
        if self.code == code and self.is_active:
            return True
        return False

    def send_invitation_to_email(self):
        send_mail(
            'Invitation', 
            'Your invitation code is ' + self.code, 
            settings.EMAIL_HOST_USER, 
            [self.receiver.email], 
            fail_silently=False
        )


class Readers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    date_readed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + ' read ' + self.book.title


class Liked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    date_liked = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + ' liked ' + self.book.title


class Author(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Translator(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    date_created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' review ' + self.book.title


class BookRawData(models.Model):
    data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)


class Book(models.Model):
    raw_data = models.JSONField(default=dict, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250, blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books', blank=True)
    translators = models.ManyToManyField(Translator, related_name='books', blank=True)
    publisher = models.ForeignKey(Publisher, related_name='books', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True,)
    pages = models.IntegerField(default=0, blank=True, null=True)
    isbn = models.CharField(max_length=255, blank=True, null=True)
    size = models.ForeignKey('Size', on_delete=models.SET_NULL, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    cover_type = models.ForeignKey('CoverType', on_delete=models.SET_NULL, blank=True, null=True)
    # And float number with max 5 and min 0
    rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], blank=True, null=True)
    goodreads_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)
    user_readers = models.ManyToManyField(User, related_name='reders_books', blank=True)
    user_liked = models.ManyToManyField(User, related_name='liked_books', blank=True)
    reviews = models.ManyToManyField(Review, related_name='books', blank=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    source_link = models.TextField(blank=True, null=True)

    def rate_book(self, user, rate):
        if user in User.objects.all():
            if not PersonRate.objects.filter(user=user, book=self).exists():
                PersonRate.objects.create(user=user, book=self, person_rate=rate)
            else:
                pr = PersonRate.objects.get(user=user, book=self)
                pr.person_rate = rate
                pr.save()

    def save(self, *args, **kwargs):

        if not self.slug:  
            # Rename image to random name
            if self.cover:
                name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12)) + '.' + self.cover.name.split('.')[-1]
                # check not exist cover name
                im = Image.open(self.cover)
                output = BytesIO()
                # Resize/modify the image to book cover size
                im.thumbnail((1200, 300), Image.ANTIALIAS)
                im.convert('RGB').save(output, format='JPEG', quality=100)
                output.seek(0)
                # change the imagefield value to be the newley modifed image value
                self.cover = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.cover.name.split('.')[0], 'image/jpeg',
                                                sys.getsizeof(output), None)

                while Book.objects.filter(cover=name).exists():
                    name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(22)) + '.' + self.cover.name.split('.')[-1]
                self.cover.name = name

            # Slugify title
            # Random 6 char slug
            slug = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            # check not exist slug
            while Book.objects.filter(slug=slug).exists():
                slug = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            self.slug = slug

        super(Book, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book:book_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class BookList(models.Model):
    """
    List of books created by specific user.
    """
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, related_name='book_lists', blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name + ' by ' + self.user.username

    def save(self, *args, **kwargs):
        # if it's not first time save slug don't change it
        if not(self.slug):
            slug = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            # if self.slug isn't unique, create new slug with random string
            while BookList.objects.filter(slug=slug).exists():
                slug = self.slug + '-' + str(random.randint(1, 2000))
            self.slug = slug
        super(BookList, self).save(*args, **kwargs)


class Size(models.Model):
    """
    Size of book.
    """
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class CoverType(models.Model):
    """
    Type of cover.
    """
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class About(models.Model):
    """
    About page.
    """
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='about/', blank=True, null=True)

    def __str__(self):
        return self.title


class Report(models.Model):
    """
    Report page or review.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, blank=True, null=True)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        # if review is not null, return review title
        if self.review:
            return f'review by: user'
        # if profile is not null, return profile username
        if self.profile:
            return self.profile.user.username
        return 'Report'


class ReportBook(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.book.title


class CategoryPosts(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category_posts/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
