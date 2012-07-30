# -*- coding: utf-8 -*-

from .models import Service
from .models import STATUS_CHOICES
from whiskerboard import USE_MONGO_DB
from django.views.generic import ListView, DetailView


import datetime


class BoardMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BoardMixin, self).get_context_data(**kwargs)
        context['statuses'] = STATUS_CHOICES.values()
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
        context['default'] = STATUS_CHOICES['ok']
        context['past'] = get_past_days(5)
        return context


class ServiceView(BoardMixin, DetailView):
    context_object_name = "service"
    model = Service
    template_name = "whiskerboard/service_detail.html"

    def get_template_names(self):
        return [self.template_name]
