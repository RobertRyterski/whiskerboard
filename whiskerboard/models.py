from datetime import datetime, date, timedelta
from django.db import models


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
    def get_absolute_url(self):
        return ('service', [self.slug])

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

#        raise NameError(results)

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


class Event(models.Model):
    service = models.ForeignKey(Service, related_name='events')
    status = models.ForeignKey(Status, related_name='events')
    message = models.TextField()
    start = models.DateTimeField(default=datetime.now)
    informational = models.BooleanField(default=False)

    class Meta:
        ordering = ('-start',)
        get_latest_by = 'start'


