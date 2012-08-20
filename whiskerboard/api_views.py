# -*- coding: utf-8 -*-
"""
The Whiskerboard API is structured (code-wise) in a similar style to the
Stashboard API and TastyPie, but uses Django's generic class-based views.

For model-based views:
Specifing a "model" only will work if mongoengine Document defines default_manager.
A custom queryset will be respected, but a "model" is needed to create and update mongo.
"""

from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson as json
from django.views.generic.base import View
from django.views.generic.edit import FormMixin, ModelFormMixin
from django.views.generic.list import MultipleObjectMixin
from whiskerboard import USE_MONGO_DB
from .models import Incident, Service, STATUS_CHOICES

# set up validation error for handling
if USE_MONGO_DB:
    from mongoengine.base import ValidationError
else:
    from django.core.exceptions import ValidationError

from .base_views import APIView


## Base API Classes


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
        # add form-based validation?
#        form = self.get_form(self.get_form_class())
        try:
            data = self.from_format(request)
        except ValidationError as e:
            return self.error(u'There was an error parsing the passed data',
                              400,
                              {'message': e.message})

        try:
            obj.from_python(**data)
        except ValidationError as e:
            return self.error(u'There was an error validating the passed data.',
                              400,
                              {'message': e.message})

        try:
            obj.save()
        except Exception as e:
            return self.error(u'There was an error saving the passed data.',
                              400,
                              {'message': e.message})

        context = {'id': unicode(obj.id),
                   'api_url': obj.get_api_url(self.version)}
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
            return self.error(u'There was an error parsing the passed data',
                              400,
                              {'message': e.message})

        try:
            self.object.from_python(**data)
        except ValidationError as e:
            return self.error(u'There was an error validating the passed data.',
                              400,
                              {'message': e.message})

        try:
            self.object.save()
        except ValidationError as e:
            return self.error(u'There was an error saving the passed data.',
                              400,
                              {'message': e.message})

#        try:
#            data = self.from_format(request)
#            self.object.from_python(**data)
#            self.object.save()
#        except ValidationError as e:
#            return self.error('Validation error')
        context = self.object.to_python(**self.get_to_python_args(method='post'))
        # maybe not 202
        return self.render_to_response(context, status=200)

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


class ServiceListView(JSONMixin, APIListView):
    model = Service
    queryset = Service.objects.all()
    context_object_name = 'services'

    def post(self, request, *args, **kwargs):
        """
        Disable creation of services on the API.
        """
        return self.http_method_not_allowed(request, *args, **kwargs)


class ServiceDetailView(JSONMixin, APIDetailView):
    model = Service
    queryset = Service.objects.all()

    def get_to_python_args(self, **kwargs):
        # if past is set to anything, it will evaluate to True
        kwargs['past'] = bool(self.request.GET.get('past'))
        return super(ServiceDetailView, self).get_to_python_args(**kwargs)


class IncidentListView(JSONMixin, APIListView):
    model = Incident
    queryset = Incident.objects.all()
    context_object_name = 'incidents'


class IncidentDetailView(JSONMixin, APIDetailView):
    model = Incident
    queryset = Incident.objects.all()


class IncidentMessageView(JSONMixin, APIDetailView):
    model = Incident
    queryset = Incident.objects.all()

    def get_to_python_args(self, **kwargs):
        kwargs['messages'] = True
        return super(IncidentMessageView, self).get_to_python_args(**kwargs)


class StatusListView(JSONMixin, APIView):
    """
    A simple view to list all the valid statuses.
    """

    def get(self, request, *args, **kwargs):
        # with priorities, would have to change if dict comprehension is not supported
#        statuses = {k:{'text':STATUS_CHOICES[k], 'priority': STATUS_PRIORITIES[k]} for k, v in STATUS_CHOICES.items()}
        # match current API doc
        context = {'statuses': STATUS_CHOICES.keys()}
        return self.render_to_response(context)
