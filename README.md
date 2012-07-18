# Whiskerboard

Whiskerboard is a status board for websites, services, and APIs, like Amazon's
[AWS status page](http://status.aws.amazon.com/).

It is heavily based on [Stashboard](http://www.stashboard.org/). Unlike
Stashboard, it uses vanilla Django, so you aren't stuck using Google App Engine.


## Quick start guide

1. Install Whiskerboard

```sh
$ git clone git@github.com:RobertRyterski/whiskerboard.git
$ cd whiskerboard
$ python setup.py install
```

2. Add Whiskerboard to your Django project

```py
# settings.py
INSTALLED_APPS = (
   # your stuff
    'whiskerboard',
)
```

```py
# urls.py
urlpatterns = patterns('',
    # simply include the whiskerboard URLs file
    url(r'^/', include('whiskerboard.urls')),
    # Admin site used to manually add Whiskerboard items
    url(r'^admin/', include(admin.site.urls)),
)
```

3. Sync and run 

```sh
$ cd your/django/project
$ python manage.py syncdb
$ python manage.py runserver
```

On the Django admin page `/admin/`, click on "services" and add the things you
want to report the status of (website, API, etc). To change the status of a
service, add an event for it.


## Why this fork?

This fork exists to bring [Whiskerboard](https://github.com/bfirsh/whiskerboard)
closer to feature parity with [Stashboard](http://www.stashboard.org/). The
main focus is the API. The Whiskerboard API should have a very similar feel
to the Stashboard API, but it's not necessarily a drop-in replacement.
