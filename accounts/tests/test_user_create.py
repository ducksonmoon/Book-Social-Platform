from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import UserProfile


class UserCreateTest(TestCase):
    """Test the user create API"""

    def test_create_user(self):
        """Test creating user"""
        client = APIClient()
        url = reverse('user:create')
        payload = {
            'name': 'احسان شکرایی',
            'username': 'EhsanShokraie',
            'email': 'mehrshad@gmail.com',
            'password': 'testpass',
        }
        response = client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=payload['username'].lower())

        self.assertEqual(user.username, payload['username'].lower())
        self.assertEqual(user.email, payload['email'].lower())
        self.assertTrue(user.check_password(payload['password']))
        self.assertEqual(user.userprofile.name, payload['name'])
