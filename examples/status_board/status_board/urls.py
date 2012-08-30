from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include('mongonaut.urls')),
    # simply include the whiskerboard URLs file
    url(r'', include('whiskerboard.urls')),
)
