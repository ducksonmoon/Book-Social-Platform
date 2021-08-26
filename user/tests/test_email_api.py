from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.test import APIClient

from core.models import ConfirmCode, UserProfile


class EmailApiTest(TestCase):
    """Test for email api."""
    def setUp(self):
        """Set up testing dependencies."""
        self.user = User.objects.create_user(
            username='test',
            email='abbas@test.com',
            password='Password1',
        )