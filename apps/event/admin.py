__author__ = 'lundberg'

from django.contrib import admin
from apps.event.models import Event, Entity, DailyEventAggregation


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'ts'
    list_display = ('ts', 'origin', 'rp', 'protocol')
    list_filter = ('protocol',)

admin.site.register(Event, EventAdmin)


class DailyEventAggregationAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'origin_name', 'rp_name', 'num_events', 'protocol')
    list_filter = ('protocol',)

admin.site.register(DailyEventAggregation, DailyEventAggregationAdmin)


class EntityAdmin(admin.ModelAdmin):
    pass

admin.site.register(Entity, EntityAdmin)