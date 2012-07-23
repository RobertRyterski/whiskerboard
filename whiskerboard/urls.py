# -*- coding: utf-8 -*-

from django.conf.urls import patterns
from django.conf.urls import url

from .views import IndexView
from .views import ServiceView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<slug>[-\w+]+)/?$', ServiceView.as_view(), name='service'),
#    url(r'^feed/?$', EventFeed(), name='feed'),
)
