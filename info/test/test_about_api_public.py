from django.test import TestCase
from django.urls import reverse


class AboutAPIPublicTest(TestCase):
    """Tesst about page"""

    def test_about_page_status_code(self):
        """Test about page status code"""
        url = reverse('info:about')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_about_page_contains_correct_html(self):
        """Test about page contains correct fields """
        url = reverse('info:about')
        response = self.client.get(url)
        # check if response contains description, title and image in serializer
        self.assertContains(response, 'title')
        self.assertContains(response, 'description')
        self.assertContains(response, 'image')
        self.assertNotContains(response, 'wrong_field')
        self.assertNotContains(response, 'id')