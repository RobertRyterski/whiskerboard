# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime

from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from mongoengine.base import ValidationError
from mongoengine.document import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import DateTimeField
from mongoengine.fields import EmbeddedDocumentField
from mongoengine.fields import ListField
from mongoengine.fields import ReferenceField
from mongoengine.fields import StringField
from mongoengine.queryset import QuerySetManager
from wsgiref.handlers import format_date_time

from .models import STATUS_CHOICES, STATUS_PRIORITIES


class Service(Document):
    # called service_name because mongoengine uses .name on fields to get their name.
    # This causes issues in mongonaut when trying to retrieve field_values.
    service_name = StringField(db_field='n', max_length=120)
    slug = StringField(db_field='s', max_length=120)
    description = StringField(db_field='d')
    tags = ListField(StringField(max_length=120), db_field='t')
    created_date = DateTimeField(db_field='cd',
                                 default=lambda: datetime.utcnow())
    _default_manager = QuerySetManager()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return str(self.service_name)

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
            'name': self.service_name,
            'url': self.get_absolute_url(),
            'api_url': self.get_api_url(version),
            'status': self.get_status(),
            'tags': self.tags
        }
        current_incidents = self.get_current_incidents()
        if current_incidents:
            obj['current_incidents'] = [unicode(i.id) for i in current_incidents]
        else:
            obj['current_incidents'] = None

        if detail:
            obj['description'] = self.description
            # check formatting
            obj['created_date'] = format_date_time(mktime(self.created_date.timetuple()))

        if past:
            past_incidents = self.get_past_incidents()
            if past_incidents:
                obj['past_incidents'] = [unicode(i.id) for i in past_incidents]
            else:
                obj['past_incidents'] = None
        return obj

    def from_python(self, **kwargs):
        if kwargs.get('name') is not None:
            self.service_name = unicode(kwargs.get('name'))
        # until user-specified slugs are supported, ignore if they get passed
        # if kwargs.get('slug') is not None:
        #    self.slug = unicode(kwargs.get('slug'))
        if kwargs.get('description') is not None:
            self.description = unicode(kwargs.get('description'))
        if kwargs.get('tags') is not None:
            self.tags = unicode(kwargs.get('tags'))
        self.validate()

    def save(self, *args, **kwargs):
        def make_slug(name):
            # For services with the same name, generate a unique slug
            slug = slugify(u'{0}'.format(name)).lower()
            new_slug = slug
            slug_count = 1
            while not Service.is_slug_available(new_slug, getattr(self, 'id', None)):
                new_slug = u'{0}-{1}'.format(slug, slug_count)
                slug_count += 1
            return new_slug

        self.slug = make_slug(self.service_name)

        super(Service, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('whiskerboard.service', kwargs={'slug': self.slug})

    def get_api_url(self, version):
        return reverse('whiskerboard.api.service.detail',
                       kwargs={'version': version, 'pk': self.pk})

    def get_current_incidents(self):
        """
        Gets incidents with this service ID and an end date > now (or none set).
        """
        return Incident.objects.filter(services=self,
                                       end_date__gt=datetime.now(),
                                       end_date=None)

    def get_past_incidents(self):
        """
        Gets all incidents with this service ID and an end date < now.
        """
        return Incident.objects.filter(services__in=self,
                                       end_date__lte=datetime.now())

    def get_status(self):
        """
        Returns the highest status from all current incidents.
        """
        incidents = self.get_current_incidents()
        if not incidents:
            return None
        statuses = [i.get_status() for i in incidents]
        # 'cause having `if i.get_status() is not None` at the end looks ugly
        statuses = [s for s in statuses if s is not None]
        if len(statuses) == 0:
            return None
        #highest = max(statuses, key=lambda x: STATUS_PRIORITIES[x])
        # this may work too
        highest = max(statuses, key=lambda x: 0 if x is None else STATUS_PRIORITIES[x])
        return highest

    @classmethod
    def is_slug_available(cls, slug, object_id=None):
        try:
            existing_slug = cls.objects.get(slug=slug)
            if existing_slug.id == object_id:
                return True
            return False
        except cls.DoesNotExist:
            return True


class Message(EmbeddedDocument):
    status = StringField(choices=STATUS_CHOICES.items(), required=True, max_length=20)
    message = StringField(required=True)
    timestamp = DateTimeField(default=lambda: datetime.utcnow(), required=True)
    _default_manager = QuerySetManager()

    def __unicode__(self):
        return str(self.message)

    def to_python(self, **kwargs):
        """
        Converts the instance to a simple Python dictionary.
        """
        # version = kwargs.pop('version', 1)
        obj = {
#            'url': self.get_absolute_url(),
#            'api_url': self.get_api_url(version),
            'status': self.status,
            'message': self.message,
            'timestamp': format_date_time(mktime(self.timestamp.timetuple())),
        }
        return obj

    def from_python(self, **kwargs):
        if kwargs.get('status') is not None:
            self.status = unicode(kwargs.get('status'))
        if kwargs.get('message') is not None:
            self.message = unicode(kwargs.get('message'))
        if kwargs.get('timestamp') is not None:
            self.timestamp = kwargs.get('timestamp')
        if kwargs.get('incident_id') is not None:
            self.incident_id = unicode(kwargs.get('incident_id'))
        self.validate()


class Incident(Document):
    # maybe use reference field?
    services = ListField(ReferenceField(Service), db_field='sid', required=True)
    title = StringField(db_field='t', required=True, max_length=300)
    messages = ListField(EmbeddedDocumentField(Message),
                         db_field='m',
                         required=True)
    start_date = DateTimeField(db_field='s',
                               default=lambda: datetime.utcnow())
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
#            'url': self.get_absolute_url(),
            'api_url': self.get_api_url(version),
            'title': self.title,
            'affected_service_ids': [unicode(serv.id) for serv in self.services],
        }

        # special messages view for incident; /api/v1/incidents/<id>/messages/
        if messages:
            if len(self.messages) > 0:
                obj['messages'] = [m.to_python(version=version) for m in self.messages]
            else:
                obj['messages'] = None
            # return now to avoid additional properties
            return obj

        # both lists and detail have these
        obj['status'] = self.get_status()
        # check formatting
        obj['start_date'] = format_date_time(mktime(self.start_date.timetuple()))

        if detail:
            latest = self.get_latest_message()
            if latest:
                obj['latest_message'] = latest.to_python(version=version,
                                                         detail=detail)
            else:
                obj['latest_message'] = None

            # check formatting
            if self.end_date:
                obj['end_date'] = format_date_time(mktime(self.end_date.timetuple())),
            else:
                obj['end_date'] = None

            obj['created_date'] = format_date_time(mktime(self.created_date.timetuple()))

        return obj

    def from_python(self, **kwargs):
        """
        Handles create and update of Incidents and their messages.
        """
        if kwargs.get('title') is not None:
            self.title = unicode(kwargs.get('title'))
        if kwargs.get('start_date') is not None:
            self.start_date = kwargs.get('start_date')
        if kwargs.get('end_date') is not None:
            self.end_date = kwargs.get('end_date')

        message = kwargs.get('message')
        status = kwargs.get('status')
        service_ids = kwargs.get('service_ids')

        # validate service_ids, make sure they exist
        # check on reference field, see if it will handle that
        # 'til then, just add 'em blindly
        self.services = service_ids

        if message is None:
            raise ValidationError('A message is required.')
        message = unicode(message)

        if status is None:
            raise ValidationError('A status is required.')
        status = unicode(status.lower())

        if status not in STATUS_CHOICES.keys():
            raise ValidationError('Status "{}" is not valid.'.format(status))

        self.messages.append(Message(message=message, status=status, incident_id=self.id))

        self.validate()

    def save(self, *args, **kwargs):
        # make sure messages are in chronological order?
        # use SortedListField?
        self.messages = sorted(self.messages, key=lambda m: m.timestamp)
        return super(Incident, self).save(*args, **kwargs)

    def get_api_url(self, version):
        return reverse('whiskerboard.api.incident.detail',
                       kwargs={'version': version, 'pk': self.pk})

    def get_status(self):
        m = self.get_latest_message()
        if m:
            return m.status
        return None

    def get_latest_message(self):
        if len(self.messages) == 0:
            return None
        self.messages.sort(key=lambda m: m.timestamp)
        return self.messages[len(self.messages) - 1]
