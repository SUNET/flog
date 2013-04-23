__author__ = 'lundberg'

from django.contrib import admin
from apps.event.models import Event, Entity


class EventAdmin(admin.ModelAdmin):
    pass

admin.site.register(Event, EventAdmin)


class EntityAdmin(admin.ModelAdmin):
    pass

admin.site.register(Entity, EntityAdmin)