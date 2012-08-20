from django.conf.urls import patterns, include, url
from django.conf import settings
#from django.contrib import admin

#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^mongonaut/', include('mongonaut.urls')),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
    # simply include the whiskerboard URLs file
    url(r'', include('whiskerboard.urls')),
)
