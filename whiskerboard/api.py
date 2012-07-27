# -*- coding: utf-8 -*-
"""
The Whiskerboard API is structured (code-wise) in a similar style to the
Stashboard API and TastyPie, but uses Django's generic class-based views.

For model-based views:
Specifing a "model" only will work iff mongoengine Document defines default_manager.
A custom queryset will be respected, but a "model" is needed to create and update mongo. 
"""

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponse
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.views.generic.edit import FormMixin, ModelFormMixin
from django.views.generic.list import MultipleObjectMixin
from .models import Message, Incident, Service

# define __all__ to avoid a long, messy import in urls.py
__all__ = [
    'APIIndexView',
    'ServiceListView',
    'ServiceDetailView',
    'IncidentListView',
    'IncidentDetailView',
#    'StatusListView',
]

## Base API Classes


class APIView(View):
    """
    A class to cover base functionality of the API.

    Assumes a mixin defines content_type, to_format, and from_format.
    Assumes to_python and from_python methods exist on the models.
    """
    response_class = HttpResponse
    version = 1

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # version check?
        self.version = int(kwargs.pop('version', 1))
        # future: apply throttling
        # check authentication (OAuth)
        return super(APIView, self).dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a formatted response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = self.content_type
        return self.response_class(self.to_format(context), **response_kwargs)

    def error(self, message, status=400, context={}):
        """
        Returns an error with the specified message and status code.
        Additional info can be passed in with context.
        """
        context.update({'error': message})
        return self.render_to_response(context, status=status)

    def get_to_python_args(self, **kwargs):
        """
        A hook for advanced options when calling model.to_python.
        """
        kwargs['version'] = self.version
        return kwargs


class APIListView(APIView, FormMixin, MultipleObjectMixin):
    """
    A view for the root level of an object.
    GET -- show list of objects
    POST -- create new object, return new object
    PUT, DELETE, etc. -- not allowed

    Currently no pagination or allow_empty support.
    """
    def get_queryset(self):
        """
        A mongoengine-friendly wrapper.
        """
        try:
            return super(APIListView, self).get_queryset()
        except AttributeError:
            return self.queryset.clone()

    def get_model(self):
        if self.model is not None:
            return self.model
        if self.queryset is not None:
            queryset = self.get_queryset()
            # only Django querysets have the model property
            if hasattr(queryset, 'model'):
                return self.get_queryset().model
        raise ImproperlyConfigured('Cannot determine model from current setup.')

    def get_form(self, form_class, data=None):
        pass

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        simple_list = [obj.to_python(**self.get_to_python_args(method='get'))
                       for obj in self.object_list]
        context_object_name = self.get_context_object_name(self.object_list)
        # don't include object_list unless there is no context_object_name
        if context_object_name is not None:
            context = {context_object_name: simple_list}
        else:
            context = {'object_list': simple_list}

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # add better error messages
        obj = self.get_model()()
#        form = self.get_form(self.get_form_class())
        try:
            data = self.from_format(request)
        except ValidationError as e:
            return self.error(u'There was an error parsing the passed data')

        # form validation or model validation?

        try:
            obj.from_python(**data)
        except ValidationError as e:
            return self.error(u'There was an error validating the passed data.')

        try:
            obj.save()
        except ValidationError as e:
            return self.error(u'There was an error saving the passed data.')

        context = obj.to_python(**self.get_to_python_args(method='post'))
        return self.render_to_response(context, status=201)


class APIDetailView(APIView, ModelFormMixin):
    """
    A view for the instance level of a class.
    GET -- show the instance
    PUT -- update the instance
    DELETE -- delete the instance
    """
    def get_to_python_args(self, **kwargs):
        kwargs['detail'] = True
        return super(APIDetailView, self).get_to_python_args(**kwargs)

    def get_queryset(self):
        """
        A mongoengine-friendly wrapper.
        """
        try:
            return super(APIDetailView, self).get_queryset()
        except AttributeError:
            return self.queryset.clone()

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except:
            return self.error('Object not found.', 404)
        context = self.object.to_python(**self.get_to_python_args(method='get'))
        return self.render_to_response(context)

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            data = self.from_format(request)
        except ValidationError as e:
            return self.error(u'There was an error parsing the passed data')

        try:
            self.object.from_python(**data)
        except ValidationError as e:
            return self.error(u'There was an error validating the passed data.')

        try:
            self.object.save()
        except ValidationError as e:
            return self.error(u'There was an error saving the passed data.')

#        try:
#            data = self.from_format(request)
#            self.object.from_python(**data)
#            self.object.save()
#        except ValidationError as e:
#            return self.error('Validation error')
        context = self.object.to_python(**self.get_to_python_args(method='post'))
        # maybe not 202
        return self.render_to_response(context, status=202)

    def delete(self, request, *args, **kwargs):
        # 204
        return self.error('Not implemented.')

# A mixin must define the following:
#class FormatMixin(object):
#    content_type = None
#
#    def to_format(self, context):
#        pass
#
#    def from_format(self, request):
#        pass


class JSONMixin(object):
    """
    Based on https://docs.djangoproject.com/en/1.3/topics/class-based-views/
    """
    content_type = 'application/json'

    def to_format(self, context):
        """
        Convert the context dictionary into a JSON object.
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)

    def from_format(self, request):
        """
        Converts the POST'd data in request to JSON.
        """
        if self.content_type not in request.META['CONTENT_TYPE'].lower():
            raise ValidationError('Request content type did not match {}'.format(self.content_type))
        try:
            return json.loads(request.body.decode('utf-8'))
        except ValueError as e:
            raise ValidationError('Could not parse request data as JSON: {}'.format(str(e)))


## Whiskerboard API Implementation
class APIIndexView(JSONMixin, View):
    """
    The root of the API.
    """
    pass
#    def get(self, request, *args, **kwargs):
#        version = kwargs.pop('version')
#        context = {'msg': 'this is the API', 'version': version}
#        return self.render_to_response(context)


class IncidentListView(JSONMixin, APIListView):
    model = Incident
    queryset = Incident.objects.all()
    context_object_name = 'incidents'


class ServiceListView(JSONMixin, APIListView):
    model = Service
    queryset = Service.objects.all()
    context_object_name = 'services'


#class StatusListView(JSONMixin, APIListView):
#    queryset = Status.objects.order_by('severity')
#    context_object_name = 'statuses'


class IncidentDetailView(JSONMixin, APIDetailView):
    model = Incident
    queryset = Incident.objects.all()


class ServiceDetailView(JSONMixin, APIDetailView):
    model = Service
    queryset = Service.objects.all()

    def get_to_python_options(self, options={}):
        options['past'] = self.request.GET.get('past', False)
        return super(ServiceDetailView, self).get_format_options(options)


#class StatusDetailView(JSONMixin, APIDetailView):
#    queryset = Status.objects.all()
#    slug_url_kwarg = 'id'
