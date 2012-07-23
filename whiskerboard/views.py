import datetime
from django.views.generic import ListView, DetailView
from .models import Service, Status


class BoardMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BoardMixin, self).get_context_data(**kwargs)
        context['statuses'] = Status.objects.all()
        return context


class IndexView(BoardMixin, ListView):
    context_object_name = 'services'
    queryset = Service.objects.all()
    template_name = 'whiskerboard/index.html'

    def get_context_data(self, **kwargs):

        def get_past_days(num):
            date = datetime.date.today()
            dates = []

            for i in range(1, num + 1):
                dates.append(date - datetime.timedelta(days=i))

            return dates

        context = super(IndexView, self).get_context_data(**kwargs)
        context['default'] = Status.objects.default()
        context['past'] = get_past_days(5)
        return context


class ServiceView(BoardMixin, DetailView):
    model = Service

