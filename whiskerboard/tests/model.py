import datetime

from django.test.client import Client
from django.utils import unittest
from django.utils import simplejson as json

from whiskerboard.models import Service, Incident, Message

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

    # def test_to_python(self):
        # pass

    # def test_from_python(self):
        # pass
    
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
        
        # if there are no incidents affecting the service, status is unknown
        self.assertIsNone(s.get_status())
        
        # if there is only an incident with an unknown status affecting this service, status is unknown
        unknown_incident = Incident.objects.create(title='An Unknown Incident', services=[s])
        self.assertIsNone(s.get_status())
        
        # if there are multiple incidents affecting this service, the highest priority / "worst" status wins
        m = Message(status='ok', message='okay')
        ok_incident = Incident.objects.create(title='An OK Incident', services=[s], messages=[m])
        m = Message(status='warning', message='warning!')
        warning_incident = Incident.objects.create(title='A Warning Incident', services=[s], messages=[m])
        m = Message(status='down', message='down!')
        down_incident = Incident.objects.create(title='A Down Incident', services=[s], messages=[m])
        m = Message(status='info', message='update')
        info_incident = Incident.objects.create(title='An Info Incident', services=[s], messages=[m])
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
        
