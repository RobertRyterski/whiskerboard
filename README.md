# Whiskerboard

Whiskerboard is a status board for websites, services, and APIs, like Amazon's
[AWS status page](http://status.aws.amazon.com/).

It is heavily based on [Stashboard](http://www.stashboard.org/). Unlike
Stashboard, it uses vanilla Django, so you aren't stuck using Google App Engine.


## Example

We've created an example project complete with CSS and images for testing.
There isn't any sample data currently, so you'll have to add your own.

It's pretty easy to set up:
    ```sh
    $ git clone git@github.com:RobertRyterski/whiskerboard.git
    $ cd whiskerboard/example
    $ sudo pip install -r requirements.txt
    $ cd ..
    $ python manage.py syncdb
    $ python manage.py runserver
    ```

## Install

If you'd rather install Whiskerboard as a reusable Django app, use setup.py:

   ```sh
   $ git clone git@github.com:RobertRyterski/whiskerboard.git
   $ cd whiskerboard
   $ python setup.py install
   ```

Toss Whiskerboard in your project's `INSTALLED_APPS`:

   ```py
   # settings.py
   INSTALLED_APPS = (
      # your stuff
       'whiskerboard',
   )
   ```
   
Add an an include for your URL patterns:

   ```py
   # urls.py
   urlpatterns = patterns('',
       # simply include the whiskerboard URLs file
       url(r'^/', include('whiskerboard.urls')),
       # Admin site used to manually add Whiskerboard items
       url(r'^admin/', include(admin.site.urls)),
   )
   ```
> _Note_: The admin site is only required if you want to manually add items without the API.

Finally, sync and run:
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
