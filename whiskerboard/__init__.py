# -*- coding: utf-8 -*-


from django.conf import settings

USE_MONGO_DB = getattr(settings, 'USE_MONGO_DB', False)
