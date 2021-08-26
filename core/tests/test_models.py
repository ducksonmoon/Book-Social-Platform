from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File

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
        defu_avatar = 'defaults/avatar.png'
        self.assertEqual(user_profile.avatar.name, defu_avatar)

    def test_user_profile_model_avatar_upload(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        import os
        path = 'avatars/SG.png'
        add = os.path.join(settings.MEDIA_ROOT, path)
        user_profile.avatar = add
        user_profile.save()
        user_profile.refresh_from_db()
        # check if avatar is changed
        self.assertNotEqual(user_profile.avatar.name, 'avatar.png')
        self.assertEqual(user_profile.avatar.name, add)
    
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

    def test_user_profile_follow(self):
        new_user = User.objects.create_user(
            username='testuser2', password='12345')

        user_profile1 = UserProfile.objects.create(
            user=self.user,
            name='Abbas Ali',
        )
        user_profile2 = UserProfile.objects.create(
            user=new_user,
            name='Babr Ali',
        )

        user_profile1.follow(user_profile2)
        self.assertEqual(user_profile1.following.count(), 1)
        self.assertEqual(user_profile1.following.first().userprofile, user_profile2)
        self.assertEqual(user_profile2.followers.count(), 1)
        self.assertEqual(user_profile2.followers.first().userprofile, user_profile1)
    
    def test_user_profile_unfollow(self):
        new_user = User.objects.create_user(
            username='testuser2', password='12345')
        
        user_profile1 = UserProfile.objects.create(
            user=self.user,
            name='Abbas Ali',
        )
        user_profile2 = UserProfile.objects.create(
            user=new_user,
            name='Babr Ali',
        )

        user_profile1.follow(user_profile2)
        user_profile1.unfollow(user_profile2)
        user_profile1.following.remove(user_profile2.user)

        self.assertEqual(user_profile1.following.count(), 0)
        self.assertEqual(user_profile2.followers.count(), 0)

    def test_user_profile_follow_my_user(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        user_profile.follow(user_profile)
        self.assertEqual(user_profile.following.count(), 0)
        self.assertEqual(user_profile.followers.count(), 0)

    def test_user_profile_follow_unfollow_my_user(self):
        user_profile = UserProfile.objects.create(
            user=self.user,
            name='Babr Ali',
        )
        user_profile.follow(user_profile)
        user_profile.unfollow(user_profile)
        self.assertEqual(user_profile.following.count(), 0)
        self.assertEqual(user_profile.followers.count(), 0)
    
    def test_user_profile_follow__twice(self):
        new_user = User.objects.create_user(
            username='testuser2', password='12345')
        
        user_profile1 = UserProfile.objects.create(
            user=self.user,
            name='Abbas Ali',
        )
        user_profile2 = UserProfile.objects.create(
            user=new_user,
            name='Babr Ali',
        )

        user_profile1.follow(user_profile2)
        user_profile1.follow(user_profile2)
        self.assertEqual(user_profile1.following.count(), 1)
        self.assertEqual(user_profile1.following.first().userprofile, user_profile2)
        self.assertEqual(user_profile2.followers.count(), 1)
        self.assertEqual(user_profile2.followers.first().userprofile, user_profile1)
