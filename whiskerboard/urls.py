# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.simple import redirect_to

from .api_urls import urls as api_urls
from .views import IndexView, ServiceView


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='whiskerboard.index'),
    url(r'^services/?$', redirect_to, {'url': reverse_lazy('whiskerboard.index')}),
    url(r'^services/(?P<slug>[-\w]+)/?$', ServiceView.as_view(), name='whiskerboard.service'),
    url(r'^api/?$', redirect_to,
        {'url': reverse_lazy(
            'whiskerboard.api.index',
            kwargs={'version': '1'})
        }),
    url(r'^api/v(?P<version>\d+)/', include(api_urls)),
)
