# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from whiskerboard import USE_MONGO_DB

STATUS_CODES = {
    'ok': {'text': _('OK'), 'db_key': 'ok', 'priority': 0},
    'info': {'text': _('Info'), 'db_key': 'ok', 'priority': 10},
    'warning': {'text': _('Warning'), 'db_key': 'ok', 'priority': 20},
    'down': {'text': _('Down'), 'db_key': 'ok', 'priority': 30}
}

if USE_MONGO_DB:
    from mongo_models import *
else:
    from sql_models import *
