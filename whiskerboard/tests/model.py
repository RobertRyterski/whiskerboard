import datetime

from django.test.client import Client
from django.utils import unittest
from django.utils import simplejson as json

from mongoengine.base import ValidationError

from mock import patch

from whiskerboard.models import Service, Incident, Message, format_date

class ServiceModelTestCase(unittest.TestCase):
    """
    Tests on the Service model functions.
    """

    def setUp(self):
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

    def test_unicode(self):
        # testing __unicode__ is really just testing str()
        self.assertEqual(str('A Service'), self.services[0].__unicode__())

    def test_to_python_standard_base(self):
        s = self.services[0]
        obj = s.to_python()
        
        # make sure all the keys in the standard view are present
        keys = ['id', 'name', 'url', 'api_url', 'status', 'tags', 'current_incidents']
        self.assertItemsEqual(keys, obj.keys())
        
        # make sure the values match
        # (duplicates a lot of code)
        self.assertEqual(obj['id'], unicode(s.id))
        self.assertEqual(obj['name'], s.service_name)
        self.assertEqual(obj['url'], s.get_absolute_url())
        self.assertEqual(obj['api_url'], s.get_api_url(1))
        self.assertEqual(obj['status'], s.get_status())
        self.assertEqual(obj['tags'], s.tags)

        self.assertNotIn('description', obj.keys())
        self.assertNotIn('created_date', obj.keys())
        self.assertNotIn('past_incidents', obj.keys())
        
    def test_to_python_with_current_incidents(self):
        s = self.services[0]
        obj = s.to_python()
        incidents = s.get_current_incidents()
        
        self.assertEqual(len(incidents), len(obj['current_incidents']))
        for i in incidents:
            self.assertIn(unicode(i.id), obj['current_incidents'])
        
    
    def test_to_python_without_current_incidents(self):
        s = Service.objects.create(service_name='Empty Service')
        obj = s.to_python()        
        self.assertIsNone(obj['current_incidents'])
        
    def test_to_python_detail(self):
        s = self.services[0]
        obj = s.to_python(detail=True)
        
        self.assertIn('description', obj.keys())
        self.assertIn('created_date', obj.keys())
        
        self.assertEqual(obj['description'], s.description)
        self.assertEqual(obj['created_date'], format_date(s.created_date))
        
        
    def test_to_python_with_past_incidents(self):
        s = self.services[0]
        obj = s.to_python(past=True)
        
    def test_to_python_without_past_incidents(self):
        s = Service.objects.create(service_name='Empty Service')
        obj = s.to_python(past=True)
        

    def test_from_python(self):
        s = Service.objects.create(service_name='Test Service', description='Test Service', tags=['a', 'b'])
        s.from_python(service_name='name', description='description', tags=['tags'])
        self.assertEqual(s.service_name, 'name')
        self.assertEqual(s.description, 'description')
        self.assertEqual(s.tags, ['tags'])
    
    # make_slug is defined in save
    def test_make_slug_on_save(self):
        s = Service(service_name='unique service')
        self.assertIsNone(s.slug)
        s.save()
        self.assertIsNotNone(s.slug)
        
    def test_make_slug_duplicate(self):
        a = Service.objects.create(service_name='unique service')
        b = Service.objects.create(service_name='unique service')
        self.assertNotEqual(a.slug, b.slug)

    def test_get_absolute_url(self):
        # basically testing Django's reverse function
        s = Service.objects.create(service_name='example service')
        # weak test
        self.assertIn(s.slug, s.get_absolute_url())
        
    def test_get_api_url(self):
        # bascially testing Django's reverse function
        s = Service.objects.create(service_name='example service')
        version = 1
        # weak test
        self.assertIn(str(s.pk), s.get_api_url(version))

    def test_get_current_incidents(self):
        # current incidents = incidents that impact service in question and (end > now or end unknown)
        current = self.services[0].get_current_incidents()
        
        # no incidents
        s = Service.objects.create(service_name='an uneventful service')
        self.assertEqual(len(s.get_current_incidents()), 0)
        
        # end < now
        self.assertNotIn(self.incidents[0], current)
        
        # end = now
        
        # end > now
        self.assertIn(self.incidents[2], current)
        
        # end unknown
        self.assertIn(self.incidents[1], current)

    def test_get_past_incidents(self):
        # past incidents = incidents that impact service in question and end <= now
        past = self.services[0].get_past_incidents()
        
        # no incidents
        s = Service.objects.create(service_name='an uneventful service')
        self.assertEqual(len(s.get_past_incidents()), 0)
        
        # end < now
        self.assertIn(self.incidents[0], past)
        
        # end = now
        
        # end > now
        self.assertNotIn(self.incidents[2], past)
        
        # end unknown
        self.assertNotIn(self.incidents[1], past)

    def test_get_status(self):
        s = Service.objects.create(service_name='A Troubled Service')
        
        unknown_incident = MockIncident(None)
        ok_incident = MockIncident('ok')
        warning_incident = MockIncident('warning')
        down_incident = MockIncident('down')
        info_incident = MockIncident('info')
        
        with patch.object(s, 'get_current_incidents') as patched_method:        
            # if there are no incidents affecting the service, status is unknown        
            self.assertIsNone(s.get_status())
            
            # if there is only an incident with an unknown status affecting this service, status is unknown
            patched_method.return_value = [unknown_incident]
            self.assertIsNone(s.get_status())
            
            # if there are multiple incidents affecting this service, the highest priority / "worst" status wins
            patched_method.return_value = [unknown_incident, ok_incident, warning_incident, down_incident, info_incident]
            self.assertEqual('down', s.get_status())

    def test_is_slug_available_new_slug(self):
        # make sure the slug doesn't exist first
        self.assertRaises(Service.DoesNotExist, Service.objects.get, slug='a fake slug')
        # now test
        self.assertTrue(Service.is_slug_available('a fake slug'))
        
    def test_is_slug_available_existing_owner(self):
        """
        As long as make_slug is run on save, the owner of a slug should always see that slug as available.
        """
        s = Service.objects.create(service_name='existing owner slug test service')
        self.assertTrue(Service.is_slug_available(s.slug, s.pk))
        
    def test_is_slug_available_existing(self):
        """
        Test that an existing slug is not availble to a non-owning service.
        """
        a = Service.objects.create(service_name='existing slug test service a')
        b = Service.objects.create(service_name='existing slug test service b')
        self.assertFalse(Service.is_slug_available(a.slug))
        self.assertFalse(Service.is_slug_available(a.slug, b.pk))
    
class IncidentModelTestCase(unittest.TestCase):
    """
    Tests on the Incident model functions.
    """
    
    def test_unicode(self):
        i = Incident(title='An Incident')
        self.assertEqual(str('An Incident'), i.__unicode__())
        
    def test_to_python_base(self):
        s = Service.objects.create(service_name='A Service')
        t = datetime.datetime.now()
        m1 = Message(message='a message', timestamp=t, status='ok')
        t = t - datetime.timedelta(days=1)
        m2 = Message(message='b message', timestamp=t, status='down')
        i = Incident.objects.create(title='An Incident', services=[s], messages=[m1, m2])
        obj = i.to_python()
        
        # make sure all the keys in the standard view are present
        keys = ['id', 'title', 'api_url', 'affected_service_ids', 'status', 'start_date']
        self.assertItemsEqual(keys, obj.keys())
        
        self.assertEqual(obj['id'], str(i.pk))
        self.assertEqual(obj['api_url'], i.get_api_url(1))
        self.assertEqual(obj['title'], i.title)
        self.assertItemsEqual(obj['affected_service_ids'], [str(s.pk)])
        self.assertEqual(obj['status'], 'ok')
        self.assertEqual(obj['start_date'], None)
        
    def test_to_python_messages(self):
        i = Incident()
        obj = i.to_python(messages=True)
        
        # make sure all the keys in the messages view are present
        keys = ['id', 'title', 'api_url', 'affected_service_ids', 'messages']
        self.assertItemsEqual(keys, obj.keys())
        
        # empty messages
        self.assertEqual(i.to_python(messages=True)['messages'], None)
        
        # with messages
        s = Service.objects.create(service_name='A Service')
        t = datetime.datetime.now()
        m1 = Message(message='a message', timestamp=t, status='ok')
        t = t - datetime.timedelta(days=1)
        m2 = Message(message='b message', timestamp=t, status='down')
        i = Incident.objects.create(title='An Incident', services=[s], messages=[m1, m2])
        obj = i.to_python(messages=True)
        self.assertEqual(len(obj['messages']), 2)
        
    def test_to_python_detail(self):
        c = datetime.datetime.now() - datetime.timedelta(hours=1)
        s = datetime.datetime.now() - datetime.timedelta(minutes=1)
        e = datetime.datetime.now() - datetime.timedelta(seconds=1)
        i = Incident.objects.create(created_date=c, start_date=s, end_date=e)
        obj = i.to_python(detail=True)
        
        # make sure all the keys in the messages view are present
        keys = ['id', 'title', 'api_url', 'affected_service_ids', 'status', 'start_date', 'latest_message', 'end_date', 'created_date']
        self.assertItemsEqual(keys, obj.keys())
        
        self.assertEqual(obj['created_date'], format_date(c))
        self.assertEqual(obj['start_date'], format_date(s))
        self.assertEqual(obj['end_date'], format_date(e))
        
    def test_from_python_base(self):
        c = datetime.datetime.now() - datetime.timedelta(hours=1)
        s = datetime.datetime.now() - datetime.timedelta(minutes=1)
        e = datetime.datetime.now() - datetime.timedelta(seconds=1)
        i = Incident(title='a', created_date=c, start_date=s, end_date=e)
        
        c = datetime.datetime.now() - datetime.timedelta(hours=2)
        s = datetime.datetime.now() - datetime.timedelta(minutes=2)
        e = datetime.datetime.now() - datetime.timedelta(seconds=2)
        
        try:
            i.from_python(title='new', created_date=c, start_date=s, end_date=e)
        except ValidationError as e:
            self.fail('Validation error on basic test of Incident.from_python: ' + e.message)
        
        self.assertEqual(i.title, 'new')
        self.assertEqual(i.created_date, c)
        self.assertEqual(i.start_date, s)
        self.assertEqual(i.end_date, e)
        
    def test_from_python_with_message(self):
        i = Incident(title='a')
        
        try:
            i.from_python(message='m', status='ok')
        except ValidationError as e:
            self.fail('Validation error on message test of Incident.from_python: ' + e.message)
            
        self.assertEqual(len(i.messages), 1)
        
    def test_message_order_after_save(self):
        m1 = Message(message='3', status='down', timestamp=datetime.datetime.now() - datetime.timedelta(hours=1))
        m2 = Message(message='2', status='warning', timestamp=datetime.datetime.now())
        m3 = Message(message='1', status='ok', timestamp=datetime.datetime.now() - datetime.timedelta(days=1))
        s = Service.objects.create(service_name='A Service')
        i = Incident(title='An Incident', messages=[m1, m2, m3], services=[s])
        # if messages aren't sorted automatically
        self.assertEqual(i.messages[0], m1)
        i.save()
        self.assertEqual(i.messages[0], m3)
        self.assertEqual(i.messages[1], m1)
        self.assertEqual(i.messages[2], m2)
        
    def test_get_api_url(self):
        # bascially testing Django's reverse function
        i = Incident.objects.create(title='example incident')
        version = 1
        # weak test
        self.assertIn(str(i.pk), i.get_api_url(version))
        
    def test_get_status(self):
        i = Incident(title='An Incident')
        m = MockMessage('ok')
        with patch.object(i, 'get_latest_message') as patched_method:        
            # if there are no messages, status is unknown
            patched_method.return_value = None
            self.assertIsNone(i.get_status())
            
            # otherwise, should return the value of the latest message
            patched_method.return_value = m
            self.assertEqual(i.get_status(), 'ok')
        
    def test_get_latest_message(self):
        
        m1 = Message(message='1', status='ok', timestamp=datetime.datetime.now() - datetime.timedelta(days=1))
        m2 = Message(message='2', status='warning', timestamp=datetime.datetime.now() - datetime.timedelta(hours=1))
        m3 = Message(message='3', status='down', timestamp=datetime.datetime.now())
        s = Service.objects.create(service_name='A Service')
        i = Incident(title='An Incident', messages=[m1, m2, m3], services=[s])
        self.assertEqual(i.get_latest_message(), m3)

class MessageModelTestCase(unittest.TestCase):
    """
    Tests on the Message model functions.
    """
    
    def test_unicode(self):
        m = Message(message='A message')
        self.assertEqual(str(m.message), m.__unicode__())
        
    def test_to_python(self):
        t = datetime.datetime.now()
        m = Message(message='A message', timestamp=t, status='ok')
        obj = {'status': 'ok', 'message': 'A message', 'timestamp': format_date(t)}
        self.assertItemsEqual(obj, m.to_python())

    def test_from_python(self):
        m = Message()
        t = datetime.datetime.now()
        m.from_python(message='message', status='info', timestamp=t)
        self.assertEqual(m.message, u'message')
        self.assertEqual(m.status, u'info')
        self.assertEqual(m.timestamp, t)
    
        
class MockIncident(object):
    """
    A simplified version of Inicdent for integration testing.
    """
    
    def __init__(self, s):
        self.status = s

    def get_status(self):
        return self.status
        
class MockMessage(object):
    """
    A simplified version of Message for integration testing.
    """
    
    def __init__(self, s):
        self.status = s

    def get_status(self):
        return self.status