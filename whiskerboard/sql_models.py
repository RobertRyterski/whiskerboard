# -*- coding: utf-8 -*-
"""
This file is incredibly out of date.
"""
from datetime import datetime, date, timedelta
from time import mktime
from django.db import models
from wsgiref.handlers import format_date_time

class Category(models.Model):
    """
    A category grouping services
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_api_url(self, version):
        return ('whiskerboard.api.category.detail', (), {'version': version, 'id': self.slug})


    def to_python(self, version=1):
        obj = {
            'name': unicode(self.name),
            'id': unicode(self.slug),
            'description': unicode(self.description),
            'url': self.get_api_url(version),
        }
        return obj


class Service(models.Model):
    """
    A service to track.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='services', null=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_api_url(self, version):
        return ('whiskerboard.api.service.detail', (), {'version': version, 'id': self.slug})

    @models.permalink
    def get_absolute_url(self):
        return ('whiskerboard.service', [self.slug])

    def to_python(self, version=1, full=False):
        obj = {}
        obj['name'] = unicode(self.name)
        obj['id'] = unicode(self.slug)
        obj['description'] = unicode(self.description)
        obj['url'] = self.get_api_url(version)

        current_event = self.current_event()
        if current_event:
            obj['current-event'] = current_event.to_python(version) if full else current_event.get_api_url(version)
        else:
            obj['current-event'] = None

        if self.category:
            obj['category'] = self.category.to_python(version)
        else:
            obj['category'] = None

        return obj

    def from_python(self, **kwargs):
        fields = [f.name for f in self._meta.fields]
        for k, v in kwargs:
            if k in fields:
                setattr(self, k, v)
        self.full_clean()
        return

    def current_event(self):
        try:
            return self.events.latest()
        except Event.DoesNotExist:
            return None

    def last_five_days(self):
        """
        Used on home page.
        """
        lowest = Status.objects.default()
        severity = lowest.severity

        yesterday = date.today() - timedelta(days=1)
        ago = yesterday - timedelta(days=5)

        events = self.events.filter(start__gt=ago, start__lt=date.today())

        stats = {}

        for i in range(5):
            stats[yesterday.day] = {
                "image": lowest.image_url,
                "day": yesterday,
            }
            yesterday = yesterday - timedelta(days=1)

        for event in events:
            if event.status.severity > severity:
                if event.start.day in stats:
                    stats[event.start.day]["image"] = 'images/status/information.png'
                    stats[event.start.day]["information"] = True

        results = []

        keys = stats.keys()
        keys.sort()
        keys.reverse()

        for k in keys:
            results.append(stats[k])

        return results


class StatusManager(models.Manager):
    def default(self):
        return self.get_query_set().filter(severity=10)[0]

class Status(models.Model):
    """
    A possible system status.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.CharField(max_length=255)
    SEVERITY_CHOICES = (
        (10, 'NORMAL'),
        (30, 'WARNING'),
        (40, 'ERROR'),
        (50, 'CRITICAL'),
    )
    severity = models.IntegerField(choices=SEVERITY_CHOICES)
    image = models.CharField(max_length=100)

    objects = StatusManager()

    class Meta:
        ordering = ('severity',)
        verbose_name_plural = 'statuses'

    def __unicode__(self):
        return self.name

    def image_url(self):
        return 'images/status/{}'.format(self.image)

    @models.permalink
    def get_api_url(self, version):
        return ('whiskerboard.api.status.detail', (), {'version': version, 'id': self.slug})


    def to_python(self, version=1):
        obj = {}
        obj['name'] = unicode(self.name)
        obj['id'] = unicode(self.slug)
        obj['description'] = unicode(self.description)
        obj['url'] = self.get_api_url(version)
        # use dict.get to grab the corresponding level word or default to normal
        obj['level'] = dict(self.SEVERITY_CHOICES).get(self.severity, self.SEVERITY_CHOICES[0][1])
        obj['level-int'] = self.severity
        obj['image'] = u'not implemented'
        return obj


class Event(models.Model):
    service = models.ForeignKey(Service, related_name='events')
    status = models.ForeignKey(Status, related_name='events')
    message = models.TextField()
    start = models.DateTimeField(default=datetime.now)
    informational = models.BooleanField(default=False)

    class Meta:
        ordering = ('-start',)
        get_latest_by = 'start'

    def __unicode__(self):
        return '{}: {} {}'.format(self.service, self.status, self.start)

    @models.permalink
    def get_api_url(self, version):
        return ('whiskerboard.api.event.detail', (), {'version': version, 'id': self.id})


    def to_python(self, version=1):
        obj = {}
        obj['sid'] = unicode(self.id)
        obj['url'] = self.get_api_url(version)
        obj['timestamp'] = format_date_time(mktime(self.start.timetuple()))
        obj['status'] = self.status.to_python(version)
        obj['message'] = unicode(self.message)

        if self.informational:
            obj['informational'] = self.informational
        else:
            obj['informational'] = False

        return obj
