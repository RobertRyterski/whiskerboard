# Whiskerboard

Whiskerboard is a status board for websites, services, and APIs, like Amazon's
[AWS status page](http://status.aws.amazon.com/).

It is heavily based on [Stashboard](http://www.stashboard.org/). Unlike
Stashboard, it uses vanilla Django, so you aren't stuck using Google App Engine.

## Mongo or Sql?
This app supports using Mongo or SQL, howerver, the data models are quite different.  I recommend looking at each models.py
file and taking a look to see which is best for you.  The reason for the difference is largely based on need at the time
of creation, and the storage differences between sql and mongo.

## Settings/Configuration
If you want to use mongo as your backend set USE_MONGO_DB to true in your settings.py file as demonstrated below.

```python
USE_MONGO_DB = True
```

If you use mongo and want to have a django style admin interface look at how the example app is
setup using [mongonaut](https://github.com/pydanny/django-mongonaut)

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

3. Sync and run (only need for SQL)
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
