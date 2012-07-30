# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from whiskerboard import USE_MONGO_DB

STATUS_CHOICES = {
    'ok': _('Ok'),
    'info': _('Info'),
    'warning': _('Warning'),
    'down': _('Down')
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
