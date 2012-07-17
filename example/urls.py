from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to
from whiskerboard.feeds import EventFeed
from whiskerboard.views import IndexView, ServiceView

admin.autodiscover()

urlpatterns = patterns('',
    # redirect example site to whiskerboard
    url(r'^$', redirect_to, {'url': '/whiskerboard/'}),

    # simply include the whiskerboard URLs file
    url(r'^whiskerboard/', include('whiskerboard.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
