from django.test.client import Client
from django.utils import unittest
from django.utils import simplejson as json

from whiskerboard.models import Service

class ServiceAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_get(self):
        # HTTP 200 for GET /api/v1/services
        r = self.client.get('/api/v1/services')
        self.assertEqual(r.status_code, 200, 'GET service endpoint returns HTTP 200')
        