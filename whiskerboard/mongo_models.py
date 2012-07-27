# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime
import uuid
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from mongoengine.document import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.queryset import QuerySetManager
from mongoengine.fields import DateTimeField
from mongoengine.fields import EmbeddedDocumentField
from mongoengine.fields import ListField
from mongoengine.fields import StringField
from wsgiref.handlers import format_date_time


class Message(EmbeddedDocument):
    # id is used to keep SQL and API compatability
    id = StringField(default=lambda: uuid.uuid4().hex)
    status = StringField()
    message = StringField()
    timestamp = DateTimeField(default=lambda: datetime.utcnow())
    incident_id = StringField()  # In preparation for SQL compatability
    _default_manager = QuerySetManager()

    def __unicode__(self):
        return str(self.message)

    def to_python(self, **kwargs):
        """
        Converts the instance to a simple Python dictionary.
        """
        version = kwargs.pop('version', 1)
        obj = {
            'id': self.id,
            #'url': self.get_absolute_url(),
            #'api_url': self.get_api_url(version),
            'status': self.status,
            'message': self.message,
            'timestamp': format_date_time(mktime(self.timestamp.timetuple())),
        }
        return obj

    def from_python(self, **kwargs):
        self.status = kwargs.get('status')
        self.message = kwargs.get('message')
        self.timestamp = kwargs.get('timestamp')
        self.incident_id = kwargs.get('incident_id')
        # validate?

# currently not available
#    def get_absolute_url(self):
#        return reverse('whiskerboard.incident.message', kwargs={'id': self.id})
#
#    def get_api_url(self, version):
#        return reverse('whiskerboard.api.message.detail', kwargs={'version': version, 'pk': self.id})


class Incident(Document):
    service_ids = ListField(StringField(), db_field='sid')
    title = StringField(db_field='t')
    messages = ListField(EmbeddedDocumentField(Message), db_field='m')
    start_date = DateTimeField(db_field='s', default=lambda: datetime.utcnow())
    end_date = DateTimeField(db_field='e')
    created_date = DateTimeField(db_field='c',
                                 default=lambda: datetime.utcnow())
    _default_manager = QuerySetManager()

    def __unicode__(self):
        return str(self.title)

    def to_python(self, **kwargs):
        """
        Converts the instance to a simple Python dictionary.

        Gives a less detailed view by default, unless detail=True.
        """
        detail = kwargs.pop('detail', False)
        version = kwargs.pop('version', 1)
        messages = kwargs.pop('messages', False)
        # common attributes
        obj = {
            'id': unicode(self.id),
            'api_url': self.get_api_url(version),
            'title': self.title,
            'affected_service_ids': self.service_ids,
            'status': self.get_status(),
            # check formatting
            'start_date': format_date_time(mktime(self.start_date.timetuple())),
        }

        if detail:
            obj['latest_message'] = self.get_latest_message()
            obj['message_ids'] = [m.id for m in self.messages]
            # check formatting
            if self.end_date:
                obj['end_date'] = format_date_time(mktime(self.end_date.timetuple())),
            else:
                obj['end_date'] = None
            obj['created_date'] = format_date_time(mktime(self.created_date.timetuple()))

        if messages:
            obj['messages'] = [m.to_python(version=version) for m in self.messages]

        return obj

    def from_python(self, **kwargs):
        self.service_ids = kwargs.get('service_ids')
        self.title = kwargs.get('title')

        pass

    def get_absolute_url(self):
#        return reverse('whiskerboard.incident', kwargs={'id': self.slug})
        return 'Not implemented.'

    def get_api_url(self, version):
        return reverse('whiskerboard.api.incidents.detail', kwargs={'version': version, 'pk': self.pk})

    def get_status(self):
        return 'Not implemented.'

    def get_latest_message(self):
        return 'Not implemented.'


class Service(Document):
    name = StringField(db_field='n')
    slug = StringField(db_field='s')
    description = StringField(db_field='d')
    tags = StringField(db_field='t')
    created_date = DateTimeField(db_field='cd',
                                 default=lambda: datetime.utcnow())
    _default_manager = QuerySetManager()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return str(self.name)

    def to_python(self, **kwargs):
        """
        Converts the instance to a simple Python dictionary.

        Gives a less detailed view by default, unless detail=True.
        """
        detail = kwargs.pop('detail', False)
        version = kwargs.pop('version', 1)
        past = kwargs.pop('past', False)

        # common attributes
        obj = {
            'id': unicode(self.id),
            'name': self.name,
            'url': self.get_absolute_url(),
            'api_url': self.get_api_url(version),
            'status': self.get_status(),
            'tags': self.tags
        }
        current_incidents = self.get_current_incidents()
        if current_incidents:
            obj['current_incidents'] = [i.id for i in current_incidents]
        else:
            obj['current_incidents'] = None

        if detail:
            obj['description'] = self.description
            # check formatting
            obj['created_date'] = format_date_time(mktime(self.created_date.timetuple()))

        if past:
            past_incidents = self.get_past_incidents()
            if past_incidents:
                obj['past_incidents'] = [i.id for i in past_incidents]
            else:
                obj['past_incidents'] = None
        return obj

    def from_python(self, **kwargs):
        self.name = kwargs.get('name')
        # until user-specified slugs are supported, ignore if they get passed
        #self.slug = kwargs.get('slug')
        self.description = kwargs.get('description')
        self.tags = kwargs.get('tags')
        # validation?
        return

    def save(self, *args, **kwargs):
        def make_slug(name):
            # For services with the same name, generate a unique slug
            slug = slugify(u'{0}'.format(name)).lower()
            slug_count = 1
            while not self.is_slug_available(slug):
                slug = u'{0}{1}'.format(slug, slug_count)
                slug_count += 1
            return slug

        if not self.id:
            self.slug = make_slug(self.name)

        super(Service, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('whiskerboard.service', kwargs={'slug': self.slug})

    def get_api_url(self, version):
        return reverse('whiskerboard.api.service.detail', kwargs={'version': version, 'pk': self.pk})

    def get_current_incidents(self):
        return None

    def get_past_incidents(self):
        return None

    def get_status(self):
        return 'Not implemented.'

    @classmethod
    def is_slug_available(cls, slug):
        try:
            cls.objects.get(slug=slug)
            return False
        except cls.DoesNotExist:
            return True
