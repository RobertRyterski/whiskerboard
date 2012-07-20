# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.translation import ugettext as _


STATUS_CODES = {'ok': _('Ok'),
                'info': _('Info'),
                'warning': _('Warning'),
                'error': _('Error')}

if getattr(settings, 'USE_MONGO_DB', False):
    from mongo_models import *
else:
    from sql_models import *
