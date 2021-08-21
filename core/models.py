from django.db import models
from django.contrib.auth.models import User

from PIL import Image

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='media/avatars/', blank=True, default='media/defaults/avatar.png')
    SOCIAL_MEDIA_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'Linkedin'),
    )
    social_media_username = models.CharField(max_length=255, blank=True, choices=SOCIAL_MEDIA_CHOICES)
    social_media_link = models.URLField(blank=True)

    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following', blank=True)

    # readed_books = models.ManyToManyField('Book', related_name='readed_books', blank=True) 

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
    
    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        # Resize the image to a square
        if self.avatar:
            img = Image.open(self.avatar)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

    def __str__(self):
        return self.user.username
