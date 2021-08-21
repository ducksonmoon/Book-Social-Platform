from core.models import UserProfile
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


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
