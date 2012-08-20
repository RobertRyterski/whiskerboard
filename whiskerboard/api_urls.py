# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .api_views import APIIndexView
from .api_views import IncidentDetailView
from .api_views import IncidentListView
from .api_views import IncidentMessageView
from .api_views import ServiceListView
from .api_views import ServiceDetailView
from .api_views import StatusListView


urls = patterns('',
    url(r'^$', APIIndexView.as_view(),
        name='whiskerboard.api.index'),
    url(r'^services/?$', ServiceListView.as_view(),
        name='whiskerboard.api.service.list'),
    url(r'^services/(?P<pk>[\w]+)/?$', ServiceDetailView.as_view(),
        name='whiskerboard.api.service.detail'),
    url(r'^incidents/?$', IncidentListView.as_view(),
        name='whiskerboard.api.incident.list'),
    url(r'^incidents/(?P<pk>[\w]+)/?$', IncidentDetailView.as_view(),
        name='whiskerboard.api.incident.detail'),
    url(r'^incidents/(?P<pk>[\w]+)/messages/?$', IncidentMessageView.as_view(),
        name='whiskerboard.api.incident.message'),
    url(r'^statuses/?$', StatusListView.as_view(),
        name='whiskerboard.api.status.list'),
)
