from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # simply include the whiskerboard URLs file
    url(r'', include('whiskerboard.urls')),

    # Admin site used to manually add Whiskerboard items
    url(r'^admin/', include(admin.site.urls)),
)
