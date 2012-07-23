from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to
from .feeds import EventFeed
from .views import IndexView, ServiceView

urlpatterns = patterns('',
    url(r'^$',
        IndexView.as_view(),
        name='whiskerboard.index'),
    url(r'^services/?$',
        redirect_to,
        {'url': reverse_lazy('whiskerboard.index')}),
    url(r'^services/(?P<slug>[-\w]+)/?$',
        ServiceView.as_view(),
        name='whiskerboard.service'),
    url(r'^feed/?$',
        EventFeed(),
        name='whiskerboard.feed'),
)
