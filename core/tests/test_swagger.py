from django.test import TestCase
from django.urls import reverse

# Test swagger is runnig ok
class TestSwagger(TestCase):
    def test_swagger(self):
        response = self.client.get(reverse('schema-swagger-ui'))
        self.assertEqual(response.status_code, 200)
    
    def test_swagger_redoc(self):
        response = self.client.get(reverse('schema-redoc'))
        self.assertEqual(response.status_code, 200)

