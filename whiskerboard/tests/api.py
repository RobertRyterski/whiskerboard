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

    def test_root_get_status(self):
        # HTTP 200 for GET /api/v1/services
        r = self.client.get('/api/v1/services')
        self.assertEqual(r.status_code, 200, 'GET service endpoint returns HTTP 200')

    def test_root_post_no_data_status(self):
        # HTTP 405 for POST /api/v1/services with no data
        r = self.client.post('/api/v1/services')
        self.assertEqual(r.status_code, 405, 'POST (with no data) service endpoint returns HTTP 405')
        
    def test_root_post_valid_data_status(self):
        # HTTP 201 for POST /api/v1/services with valid data
        r = self.client.post('/api/v1/services', content='{service_name: "A Service"}', content_type='application/json;charset=utf-8')
        self.assertEqual(r.status_code, 201, 'POST (with valid data) service endpoint returns HTTP 405')
        
    def test_root_post_invalid_data_status(self):
        # HTTP 400 for POST /api/v1/services with invalid data
        r = self.client.post('/api/v1/services', content='{thing: "value"}')
        self.assertEqual(r.status_code, 201, 'POST (with valid data) service endpoint returns HTTP 405')

    def test_root_delete_status(self):
        # HTTP 405 for DELETE /api/v1/services
        r = self.client.delete('/api/v1/services')
        self.assertEqual(r.status_code, 405, 'DELETE service endpoint returns HTTP 405')

    def test_root_put(self):
        # HTTP 405 for PUT /api/v1/services
        r = self.client.put('/api/v1/services')
        self.assertEqual(r.status_code, 405, 'PUT service endpoint returns HTTP 405')


    # Services CRUD

    def test_root_get_content(self):
        r = self.client.get('/api/v1/services')
        rJson = json.loads(r.content)
        i = 0
        for s in self.services:
            self.assertEquals(s.service_name, rJson["services"][i]["name"])
            i = i + 1

    def test_instance_get_content(self):
        r = self.client.get('/api/v1/services/' + str(self.services[0].id))
        rJson = json.loads(r.content)
        self.assertEquals(self.services[0].service_name, rJson["name"])

    def test_instance_put_content(self):
        self.client.put('/api/v1/services/' + str(self.services[0].id), content='{service_name: "New A Name"}', content_type="application/json;charset=utf-8")

        services = json.loads(self.client.get('/api/v1/services/').content)["services"]
        self.assertEquals(services[0]["id"], self.services[0].id)

    def test_root_post_content(self):
        r = self.client.post('/api/v1/services/', content='{"service_name": "Test Service", "description": "Test description"}', content_type="application/json;charset=utf-8")
        self.assertTrue(r.status_code < 400)
        createdID = json.loads(r.content)["id"]
    
        foundID = false
        for service in self.client.get('/api/v1/services/')['services']:
            if service.id == createdID:
                foundID = true
                break
    
        self.assertTrue(foundID)

    # should fail, not implemented
    def test_instance_delete_valid_status(self):
        # valid request, should be HTTP 204
        s = Service.objects.create(service_name='A Service for Deletion')
        r = self.client.delete('/api/v1/services/' + str(s.id))
        self.assertEqual(r.status_code, 204)
        
    def test_instance_delete_invalid_status(self):
        # invalid request (service doesn't exist), should be HTTP 404
        r = self.client.delete('/api/v1/services/a_fake_id')
        self.assertEqual(r.status_code, 404)
    
    def test_instance_delete_valid_content(self):
        # valid request, should return deleted service
        # may change based on documentation
        s = Service.objects.create(service_name='A Service for Deletion')
        r = self.client.delete('/api/v1/services/' + str(s.id))
        self.assertIn(str(s.id), r.content)
        
    def test_root_get_content_after_delete(self):
        s = Service.objects.create(service_name='A Service for Deletion')
        self.client.delete('/api/v1/services/' + str(s.id))
        services = json.loads(self.client.get('/api/v1/services').content)["services"]
        # go through all the services from the responce and make sure the deleted one is not in it
        for service in services:
            self.assertFalse(s.id, service["id"])

class IncidentAPITestCase(unittest.TestCase):
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
    
    # Incidents CRUD

    def test_root_get_content(self):
        incidents = json.loads(self.client.get('/api/v1/incidents/').content)["incidents"]

        for i in range(0,len(self.incidents)):
            incidents[i]['id'] == self.incidents[i].id

    # should fail, not implimented
    def test_root_get_content_after_delete(self):
        self.client.delete('/api/v1/incidents/' + str(self.incidents[0].id))
        incidents = json.loads(self.client.get('/api/v1/incidents').content)["incidents"]
        # go through all the services from the responce and make sure the deleted one is not in it
        for incident in incidents:
            self.assertFalse(self.incidents[0].id, incident["id"])

    def test_root_post_valid_data_content(self):
        r = self.client.post('/api/v1/incidents/', content='{"service_ids": ["' + str(self.services[0].id) + '"], "title": "test incident", "message": "test message", "status": "down", "start_date": "2012-03-12T10:36Z"}', content_type="application/json;charset=utf-8")
        j = json.loads(r.content)
        
        self.assertIn('id', j.keys())
            
        foundID = false
        for incident in self.client.get('/api/v1/incidents/')['incidents']:
            if incident.id == createdID:
                foundID = true
                break
    
        self.assertTrue(foundID)

    def test_instance_put_valid_data(self):
        self.client.put('/api/v1/incidents/' + str(self.incidents[0].id), content='{"message": "ITS DOWN"}', content_type="application/json;charset=utf-8")
        
        incidents = json.loads(self.client.get('/api/v1/incidents/').content)["incidents"]
        self.assertEquals(incidents[0]["id"], self.incidents[0].id)

class StatusAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_get_status(self):
        r = self.client.get('/api/v1/statuses')
        self.assertEqual(r.status_code, 200)

    def test_root_post_status(self):
        r = self.client.post('/api/v1/statuses')
        self.assertEqual(r.status_code, 405)

    def test_root_put_status(self):
        r = self.client.put('/api/v1/statuses')
        self.assertEqual(r.status_code, 405)

    def test_root_delete_status(self):
        r = self.client.delete('/api/v1/statuses')
        self.assertEqual(r.status_code, 405)
    
    def test_root_get_content(self):
        r = self.client.get('/api/v1/statuses')
        statuses = json.loads(r.content)["statuses"]

        self.assertIn('ok', statuses)
        self.assertIn('down', statuses)
        self.assertIn('warning', statuses)
        self.assertIn('info', statuses)
