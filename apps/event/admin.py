__author__ = 'lundberg'

from django.contrib import admin
from apps.event.models import Country, Event, Entity, DailyEventAggregation, EduroamEvent, EduroamRealm


class CountryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Country, CountryAdmin)


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


class EduroamEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'ts'
    list_display = ('ts', 'realm', 'visited_country', 'visited_institution', 'calling_station_id', )
    list_filter = ('successful',)

admin.site.register(EduroamEvent, EduroamEventAdmin)


class EduroamRealmAdmin(admin.ModelAdmin):
    pass

admin.site.register(EduroamRealm, EduroamRealmAdmin)
