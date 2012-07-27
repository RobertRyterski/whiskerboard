# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.simple import redirect_to

from .views import IndexView, ServiceView
from .api import *

apipatterns = patterns('',
    url(r'^$',
        APIIndexView.as_view(),
        name='whiskerboard.api.index'),
    url(r'^services/?$',
        ServiceListView.as_view(),
        name='whiskerboard.api.service.list'),
    url(r'^services/(?P<pk>[\w]+)/?$',
        ServiceDetailView.as_view(),
        name='whiskerboard.api.service.detail'),
    url(r'^incidents/?$',
        IncidentListView.as_view(),
        name='whiskerboard.api.incidents.list'),
    url(r'^incidents/(?P<pk>[\w]+)/?$',
        IncidentDetailView.as_view(),
        name='whiskerboard.api.incidents.detail'),
#    url(r'^statuses/?$',
#        StatusListView.as_view(),
#        name='whiskerboard.api.status.list'),
#    url(r'^statuses/(?P<pk>[-\w]+)/?$',
#        StatusDetailView.as_view(),
#        name='whiskerboard.api.status.detail'),
)

urlpatterns = patterns('',
    url(r'^$',
        IndexView.as_view(),
        name='whiskerboard.index'),
    # might be a better way to do the redirect
    url(r'^services/?$',
        redirect_to,
        {'url': reverse_lazy('whiskerboard.index')}),
    url(r'^services/(?P<slug>[-\w]+)/?$',
        ServiceView.as_view(),
        name='whiskerboard.service'),
    url(r'^api/?$',
        redirect_to,
        {'url': reverse_lazy(
            'whiskerboard.api.index',
            kwargs={'version': '1'})
        }),
    (r'^api/v(?P<version>\d+)/', include(apipatterns)),
)
