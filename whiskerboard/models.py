# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from whiskerboard import USE_MONGO_DB

STATUS_CODES = {'ok': (_('Ok'), 0),
                'info': (_('Info'), 100),
                'warning': (_('Warning'), 200),
                'down': (_('Down'), 300)}
STATUS_DEFAULT = 'ok'

if USE_MONGO_DB:
    from mongo_models import *
else:
    from sql_models import *
