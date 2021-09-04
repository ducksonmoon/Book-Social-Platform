import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status

from core.models import UserProfile, Invitation


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
CHANGE_PASSWORD_URL = reverse('user:change_password')
MY_INVITATIONS = reverse('user:my_invitations')
INVITATION_CODE_ENTER = reverse('user:invitation_code_enter')

def create_user(**params):
    return User.objects.create_superuser(**params)


class PublicUserApiTests(TestCase):
    """ Test user api public. """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successful(self):
        """Test creating a new user"""
        payload = {
            'name': 'Abbas Masomi',
            'username': 'test1213',
            'email': 'test@tests.com',
            'password': 'ops11Paq2'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        userprofile = UserProfile.objects.get(user__username='test1213')
        self.assertEqual(userprofile.name, payload['name'])

    def test_create_token_for_user(self):
        """ Test that a token is created for the user. """
        payload = {
            'username': 'test123',
            'email': 'test@test.com',
            'password': 'Testcase123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(username='test', email='test@test.com', password='Testpass1234')
        payload = {'email': 'test@test.com', 'password': 'wrongpass1'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):
    """ Test user api private. """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username='test1213',
            email='test@test2.com',
            password='testpass1234',
        )
        self.userprofile = UserProfile.objects.create(user=self.user, name='Abbas Masomi')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(reverse('user:me'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)
    
    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'Abbas Masomi',}
        res = self.client.patch(reverse('user:me'), payload)

        self.userprofile.refresh_from_db()
        self.assertEqual(self.userprofile.name, payload['name'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_update_user_profile_with_no_name(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': '',}
        res = self.client.patch(reverse('user:me'), payload)

        self.userprofile.refresh_from_db()
        self.assertNotEqual(self.userprofile.name, payload['name'])
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password(self):
        """Test that user can change password"""
        payload = {'old_password': 'testpass1234', 'new_password': 'newpass123'}
        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['new_password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_password_with_wrong_old_password(self):
        """Test that user can change password"""
        payload = {'old_password': 'wrongpass1', 'new_password': 'newpass123'}
        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(payload['new_password']))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_no_new_password(self):
        """Test that user can change password"""
        payload = {'old_password': 'testpass1234'}
        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['old_password']))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_with_no_old_password(self):
        """Test that user can change password"""
        payload = {'new_password': 'newpass123'}
        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(payload['new_password']))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_no_payload(self):
        """Test that user can change password"""
        res = self.client.patch(CHANGE_PASSWORD_URL, {})

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('testpass1234'))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_invalid_payload(self):
        """Test that user can change password"""
        payload = {'old_password': 'testpass1234', 'new_password': '123'}
        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['old_password']))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_invalid_payload2(self):
        """Test that user can change password"""
        payload = {'old_password': 'testpass1234', 'new_password': ''}
        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['old_password']))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_invalid_payload2(self):
        """Test that user can change password"""
        payload = {'old_password': 'testpass1234', 'new_password': ' 213123124'}
        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['old_password']))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_avatar(self):
        """Test that user can change avatar"""
        # Patch a file to the endpoint
        pre = '/media/avatars/'
        path = 'avatars/SG.png'
        with open(os.path.join(settings.MEDIA_ROOT, path), 'rb') as fp:
            payload = {'avatar': fp}
            res = self.client.patch(ME_URL, payload)
        file = pre + path
        # Check that the file was uploaded
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_not_invited_user(self):
        """"Test NOT invited use"""

        res = self.client.get(MY_INVITATIONS)
        self.assertEqual(res.data['message'], 'You have no invitations.')  
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.userprofile.is_invited, False)
    
    def test_wrong_code_invited_user(self):
        """Test invited user with wrong code."""
        res = self.client.post(INVITATION_CODE_ENTER, {'code': '12345'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user.userprofile.is_invited, False)

    def test_invitation_code(self):
        """Test inviation code."""
        user_sender = User.objects.create(
            username='sender_test1213',
            email='sender_test@test2.com',
            password='testpass1234',
        )
        
        code = Invitation.objects.create(sender=user_sender)
        res = self.client.post(INVITATION_CODE_ENTER, {'code': code.code})
        code.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(code.is_active, False)
        self.assertEqual(code.receiver, self.user)
        self.assertEqual(code.sender, user_sender)
        self.assertEqual(self.user.userprofile.is_invited, True)
    
    def test_my_invitations_user(self):
        """Users 3 given invitations code."""
        user_sender = User.objects.create(
            username='sender_test1213',
            email='sender_test@test2.com',
            password='testpass1234',
        )
        code = Invitation.objects.create(sender=user_sender)
        res = self.client.post(INVITATION_CODE_ENTER, {'code': code.code})
        code.refresh_from_db()

        res = self.client.get(MY_INVITATIONS)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['invitations']), 3)
        for _ in res.data['invitations']:
            self.assertEqual(_['is_active'], True)