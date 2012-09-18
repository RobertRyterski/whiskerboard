# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


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
        self.version = int(kwargs.get('version', 1))
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
