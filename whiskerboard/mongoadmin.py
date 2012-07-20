# -*- coding: utf-8 -*-

from mongonaut.sites import MongoAdmin
from .models import Incident
from .models import Service


class ServiceAdmin(MongoAdmin):

    def has_add_permission(self, request):
        return True

    def has_edit_permission(self, request):
        return True

    def has_view_permission(self, request):
        return True

    def has_delete_permission(self, request):
        return self.has_edit_permission(request)

    search_fields = ("name",)
    list_fields = ("name", "description", "category")


Service.mongoadmin = ServiceAdmin()


class IncidentAdmin(MongoAdmin):

    def has_add_permission(self, request):
        return True

    def has_edit_permission(self, request):
        return True

    def has_view_permission(self, request):
        return True

    def has_delete_permission(self, request):
        return self.has_edit_permission(request)

    search_fields = ("title",)
    list_fields = ("messages", "start_date", "end_date", "service_ids",)


Incident.mongoadmin = IncidentAdmin()
