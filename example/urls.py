from django.conf.urls import patterns, include, url
#from django.contrib import admin

#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^mongonaut/', include('mongonaut.urls')),
    # simply include the whiskerboard URLs file
    url(r'', include('whiskerboard.urls')),
)
