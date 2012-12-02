from django.test.client import Client
from django.utils import unittest
from django.utils import simplejson as json

from whiskerboard.models import Service

class ServiceAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

        a = Service.objects.create(service_name='A Service', description='A service description.')
        b = Service.objects.create(service_name='B Service', description='B service description.')
        self.services = [a, b]

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



    def test_services_get(self):
        r = self.client.get('/api/v1/services')
        rJson = json.loads(r.content)
        i = 0
        for s in self.services:
            self.assertEquals(s.service_name, rJson["services"][i]["name"])
            i = i + 1

    def test_service_get(self):
        r = self.client.get('/api/v1/services/' + str(self.services[0].id))
        rJson = json.loads(r.content)
        self.assertEquals(self.services[0].service_name, rJson["name"])

    #def test_service_post(self):
    #    #testService = Service.objects.create(service_name='Test Service')
    #    r = self.client.post('/api/v1/services/', service_name="test service", description="test service description", slug="dfs")
    #    print r.content
    #    rr = self.client.get('/api/v1/services')
    #    print rr.content

    #def test_incident_post(self):
    #    r = self.client.post('/api/v1/incidents/', content='{"service_ids": ["' + str(self.services[0].id) + '"], "title": "test incident", "message": "test message", "status": "down", "start_date": "2012-03-12T10:36Z"}')
    #    print r.content

    #def test_incident_put(self):
    #    r = self.client.put('/api/v1/incidents/' + str(self.services[0].id), message="ITS DOWN")
    #    print r.content
    #    r = self.client.get('/api/v1/incidents/')
    #    print r.content

    def test_status_get(self):
        r = self.client.get('/api/v1/statuses')
        statuses = json.loads(r.content)["statuses"]

        self.assertEquals('ok' in statuses, True)
        self.assertEquals('down' in statuses, True)
        self.assertEquals('warning' in statuses, True)
        self.assertEquals('info' in statuses, True)
