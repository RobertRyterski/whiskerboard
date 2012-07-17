from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # simply include the whiskerboard URLs file
    url(r'^/?', include('whiskerboard.urls')),

    # Make admin site usable
    url(r'^admin/?', include(admin.site.urls)),
)
