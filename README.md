# Whiskerboard

Whiskerboard is a status board for websites, services, and APIs, like Amazon's [AWS status page](http://status.aws.amazon.com/).

It is heavily based on [Stashboard](http://www.stashboard.org/). Unlike Stashboard, it uses vanilla Django, so you aren't stuck using Google App Engine.

## Quick start guide
```
$ git clone git@github.com:RobertRyterski/whiskerboard.git
$ cd whiskerboard
$ sudo pip install -r requirements.txt
$ echo "SECRET_KEY = 'EnterABunchOfRandomCharactersHere'" > example/settings/local.py
$ ./manage.py syncdb
$ ./manage.py runserver
```

On the Django admin page `/admin/`, click on "services" and add the things you want to report the status of (website, API, etc). To change the status of a service, add an event for it.

## Why this fork?
This fork exists to bring Whiskerboard closer to feature parity with Stashboard. The main focus is the API. The Whiskerboard API should have a very similar feel to the Stashboard API, but it's not necessarily a drop-in replacement.
