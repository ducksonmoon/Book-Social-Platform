from django.test import TestCase
from django.contrib.auth.models import User

from core.models import *


class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.user.save()
    
    def test_user_model(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('12345'))
    
    def test_user_profile_model(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        self.assertEqual(user_profile.name, 'Babr Ali')
        self.assertEqual(user_profile.user, self.user)
    
    def test_user_profile_model_avatar(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        defu_avatar = 'media/defaults/avatar.png'
        self.assertEqual(user_profile.avatar, defu_avatar)

    def test_user_profile_model_avatar_upload(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        user_profile.avatar = 'media/avatars/sg.png'
        user_profile.save()
        self.assertEqual(user_profile.avatar, 'media/avatars/sg.png')
    
    def test_user_profile_model_social_media(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        user_profile.social_media = 'linkedin'
        user_profile.save()
        self.assertEqual(user_profile.social_media, 'linkedin')
    
    def test_user_profile_followers(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        self.assertEqual(user_profile.followers.count(), 0)

    def test_user_profile_following(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        self.assertEqual(user_profile.following.count(), 0)
