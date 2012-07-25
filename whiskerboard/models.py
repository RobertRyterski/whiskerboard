# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from whiskerboard import USE_MONGO_DB

STATUS_CODES = {'ok': _('Ok'),
                'info': _('Info'),
                'warning': _('Warning'),
                'down': _('Down')}

if USE_MONGO_DB:
    from mongo_models import *
else:
    from sql_models import *
