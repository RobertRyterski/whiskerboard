# -*- coding: utf-8 -*-

"""
This models file is used so the sql or mongo backend can be
dynamically loaded in based on the django application's
settings.
"""

from django.utils.translation import ugettext as _
from whiskerboard import USE_MONGO_DB

STATUS_CHOICES = {
    'ok': _(u'Ok'),
    'info': _(u'Info'),
    'warning': _(u'Warning'),
    'down': _(u'Down')
}

STATUS_PRIORITIES = {
    'ok': 0,
    'info': 10,
    'warning': 20,
    'down': 30,
}

if USE_MONGO_DB:
    from mongo_models import *
else:
    from sql_models import *
