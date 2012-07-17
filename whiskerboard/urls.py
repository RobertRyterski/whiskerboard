from django.conf.urls import patterns, include, url

from .feeds import EventFeed
from .views import IndexView
from .views import ServiceView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^services/(?P<slug>[-\w]+)$', ServiceView.as_view(), name='service'),
    url(r'^feed$', EventFeed(), name='feed'),
)
