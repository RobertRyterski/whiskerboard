from django.test.client import Client
from django.utils import unittest
from django.utils import simplejson as json
import datetime

from whiskerboard.models import Service, Incident, Message

class ServiceAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

        a = Service.objects.create(service_name='A Service', description='A service description.')
        b = Service.objects.create(service_name='B Service', description='B service description.')
        
        # started last week, ended 2 days ago
        started = datetime.datetime.now() - datetime.timedelta(days=7)
        ended = datetime.datetime.now() - datetime.timedelta(days=2)
        messages = [
            Message(status='down', timestamp=started, message='1 of i0'),
            Message(status='down', timestamp=started + datetime.timedelta(hours=3), message='2 of i0'),
            Message(status='warning', timestamp=started  + datetime.timedelta(days=1, hours=3), message='3 of i1'),
            Message(status='ok', timestamp=ended, message='4 of i0'),
            ]
        i0 = Incident.objects.create(services=[a], title='incident 0', start_date=started, end_date=ended, messages=messages)
        
        # started yesterday, end unknown
        started = datetime.datetime.now() - datetime.timedelta(days=1)
        messages = [
            Message(status='warning', timestamp=started, message='1 of i1'),
            Message(status='ok', timestamp=started + datetime.timedelta(hours=12), message='2 of i1'),
            Message(status='warning', timestamp=datetime.datetime.now(), message='3 of i1'),
            ]
        i1 = Incident.objects.create(services=[a, b], title='incident 1', start_date=started, messages=messages)

        # started earlier today, ends tomorrow
        started = datetime.datetime.now() - datetime.timedelta(hours=4)
        ended = datetime.datetime.now() + datetime.timedelta(days=1)
        messages = [
            Message(status='warning', timestamp=started, message='1 of i2'),
            Message(status='down', timestamp=started + datetime.timedelta(hours=1), message='2 of i2'),
            Message(status='down', timestamp=datetime.datetime.now() + datetime.timedelta(hours=3), message='3 of i2'),
            ]
        i2 = Incident.objects.create(services=[a, b], title='incident 2', start_date=started, messages=messages)
        
        # handy accessors for fleshed out data
        self.services = [a, b]
        self.incidents = [i0, i1, i2]

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


    # Services CRUD

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

    def test_service_put(self):
        self.client.put('/api/v1/services/' + str(self.services[0].id), content='{service_name: "New A Name"}', content_type="application/json;charset=utf-8")

        services = json.loads(self.client.get('/api/v1/services/'))["services"]
        self.assertEquals(services[0]["id"], self.services[0].id)

    def test_incident_post(self):
        r = self.client.post('/api/v1/services/', content='{"service_name": "Test Service", "description": "Test description"}', content_type="application/json;charset=utf-8")
        createdID = json.loads(r.content)["id"]
    
        foundID = false
        for service in self.client.get('/api/v1/services/')['services']:
            if service.id == createdID:
                foundID = true
                break
    
        self.assertTrue(foundID)

    # should fail, not implimented
    def test_service_delete(self):
        self.client.delete('/api/v1/services/' + str(self.services[0].id))
        services = json.loads(self.client.get('/api/v1/services').content)["services"]
        # go through all the services from the responce and make sure the deleted one is not in it
        for service in services:
            self.assertFalse(self.services[0].id, service["id"])


    # Incidents CRUD

    def test_incidents_get(self):
        incidents = json.loads(self.client.get('/api/v1/incidents/'))["incidents"]

        for i in range(0,len(self.incidents)):
            incidents[i].id == self.incidents[i].id

    # should fail, not implimented
    def test_incidents_delete(self):
        self.client.delete('/api/v1/incidents/' + str(self.incidents[0].id))
        incidents = json.loads(self.client.get('/api/v1/incidents').content)["incidents"]
        # go through all the services from the responce and make sure the deleted one is not in it
        for incident in incidents:
            self.assertFalse(self.incidents[0].id, incident["id"])

    def test_incident_post(self):
        r = self.client.post('/api/v1/incidents/', content='{"service_ids": ["' + str(self.services[0].id) + '"], "title": "test incident", "message": "test message", "status": "down", "start_date": "2012-03-12T10:36Z"}', content_type="application/json;charset=utf-8")
        createdID = json.loads(r.content)["id"]
    
        foundID = false
        for incident in self.client.get('/api/v1/incidents/')['incidents']:
            if incident.id == createdID:
                foundID = true
                break
    
        self.assertTrue(foundID)

    def test_incident_put(self):
        self.client.put('/api/v1/incidents/' + str(self.incidents[0].id), content='{"message": "ITS DOWN"}', content_type="application/json;charset=utf-8")
        
        incidents = json.loads(self.client.get('/api/v1/incidents/'))["incidents"]
        self.assertEquals(incidents[0]["id"], self.incidents[0].id)

    # Statuses R

    def test_status_get(self):
        r = self.client.get('/api/v1/statuses')
        statuses = json.loads(r.content)["statuses"]

        self.assertEquals('ok' in statuses, True)
        self.assertEquals('down' in statuses, True)
        self.assertEquals('warning' in statuses, True)
        self.assertEquals('info' in statuses, True)
