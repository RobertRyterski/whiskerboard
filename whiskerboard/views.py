# -*- coding: utf-8 -*-

<<<<<<< HEAD
from .models import Service
from .models import STATUS_CHOICES
from whiskerboard import USE_MONGO_DB
from django.views.generic import ListView, DetailView


=======
>>>>>>> master
import datetime
from django.views.generic import ListView, DetailView
from whiskerboard import USE_MONGO_DB
from .models import Service, STATUS_CODES, STATUS_DEFAULT


class BoardMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BoardMixin, self).get_context_data(**kwargs)
<<<<<<< HEAD
        context['statuses'] = STATUS_CHOICES.values()
=======
        context['statuses'] = STATUS_CODES
>>>>>>> master
        return context


class IndexView(BoardMixin, ListView):
    context_object_name = 'services'
    queryset = Service.objects.all()
    template_name = 'whiskerboard/mongo_index.html' if USE_MONGO_DB else 'whiskerboard/index.html'

    def get_context_data(self, **kwargs):

        def get_past_days(num):
            date = datetime.date.today()
            dates = []

            for i in range(1, num + 1):
                dates.append(date - datetime.timedelta(days=i))

            return dates

        context = super(IndexView, self).get_context_data(**kwargs)
<<<<<<< HEAD
        context['default'] = STATUS_CHOICES['ok']
=======
        context['default'] = STATUS_DEFAULT
>>>>>>> master
        context['past'] = get_past_days(5)
        return context


class ServiceView(BoardMixin, DetailView):
    context_object_name = "service"
    model = Service
    template_name = "whiskerboard/service_detail.html"

    def get_template_names(self):
        return [self.template_name]
