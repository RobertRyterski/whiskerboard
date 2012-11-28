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

    def test_root_post(self):
        # HTTP 405 for POST /api/v1/services
        r = self.client.post('/api/v1/services')
        self.assertEqual(r.status_code, 405, 'POST service endpoint returns HTTP 405')

    def test_root_delete(self):
        # HTTP 405 for DELETE /api/v1/services
        r = self.client.delete('/api/v1/services')
        self.assertEqual(r.status_code, 405, 'DELETE service endpoint returns HTTP 405')

    def test_root_put(self):
        # HTTP 405 for PUT /api/v1/services
        r = self.client.put('/api/v1/services')
        self.assertEqual(r.status_code, 405, 'PUT service endpoint returns HTTP 405')
        