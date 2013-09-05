__author__ = 'lundberg'

from django.contrib import admin
from apps.event.models import Country, Event, Entity, EduroamEvent, EduroamRealm


class CountryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Country, CountryAdmin)


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'ts'
    list_display = ('ts', 'origin', 'rp', 'protocol')
    list_filter = ('protocol',)

admin.site.register(Event, EventAdmin)


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