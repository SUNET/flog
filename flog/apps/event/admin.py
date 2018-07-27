from __future__ import absolute_import

from django.contrib import admin
from django.core.paginator import Paginator
from django.db import connection
from flog.apps.event.models import Country, Event, Entity, DailyEventAggregation
from flog.apps.event.models import EduroamEvent, EduroamRealm, DailyEduroamEventAggregation
from flog.apps.event.models import OptimizedDailyEduroamEventAggregation

import logging

logger = logging.getLogger(__name__)

__author__ = 'lundberg'


class LargeTablePaginator(Paginator):
    """
    Warning: Postgresql only hack
    Overrides the count method of QuerySet objects to get an estimate instead of actual count when not filtered.
    However, this estimate can be stale and hence not fit for situations where the count of objects actually matter.
    """

    def _get_count(self):
        if getattr(self, '_count', None) is not None:
            return self._count

        query = self.object_list.query
        if not query.where:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT reltuples FROM pg_class WHERE relname = %s",
                               [query.model._meta.db_table])
                self._count = int(cursor.fetchone()[0])
            except Exception as e:
                logger.debug('Exception in LargeTablePaginator')
                logger.debug(e)
                self._count = super(LargeTablePaginator, self)._get_count()
        else:
            self._count = super(LargeTablePaginator, self)._get_count()

        return self._count

    count = property(_get_count)


class CountryAdmin(admin.ModelAdmin):

    class Meta:
        ordering = ['name']


admin.site.register(Country, CountryAdmin)


class EventAdmin(admin.ModelAdmin):
    paginator = LargeTablePaginator
    show_full_result_count = False
    list_display = ('ts', 'origin', 'rp', 'protocol')
    list_filter = ('ts', 'protocol', 'origin', 'rp')


admin.site.register(Event, EventAdmin)


class DailyEventAggregationAdmin(admin.ModelAdmin):
    paginator = LargeTablePaginator
    show_full_result_count = False
    date_hierarchy = 'date'
    list_display = ('date', 'origin_name', 'rp_name', 'num_events', 'protocol')
    list_filter = ('protocol',)
    search_fields = ('origin_name', 'rp_name',)


admin.site.register(DailyEventAggregation, DailyEventAggregationAdmin)


class EntityAdmin(admin.ModelAdmin):
    pass


admin.site.register(Entity, EntityAdmin)


class EduroamEventAdmin(admin.ModelAdmin):
    paginator = LargeTablePaginator
    show_full_result_count = False
    list_display = ('ts', 'realm', 'visited_country', 'visited_institution', 'calling_station_id', )
    list_filter = ('ts', 'successful',)


admin.site.register(EduroamEvent, EduroamEventAdmin)


class DailyEduroamEventAggregationAdmin(admin.ModelAdmin):
    paginator = LargeTablePaginator
    show_full_result_count = False
    date_hierarchy = 'date'
    list_display = ('date', 'realm_country', 'realm', 'visited_country', 'visited_institution', 'calling_station_id')
    list_filter = ('realm_country', 'visited_country',)


admin.site.register(DailyEduroamEventAggregation, DailyEduroamEventAggregationAdmin)


class OptimizedDailyEduroamEventAggregationAdmin(admin.ModelAdmin):
    paginator = LargeTablePaginator
    show_full_result_count = False
    date_hierarchy = 'date'
    list_display = ('date', 'realm', 'visited_institution', 'calling_station_id_count')
    list_filter = ('realm__country', 'visited_institution__country',)
    search_fields = ('realm', 'visited_institution',)


admin.site.register(OptimizedDailyEduroamEventAggregation, OptimizedDailyEduroamEventAggregationAdmin)


class EduroamRealmAdmin(admin.ModelAdmin):
    list_display = ('realm', 'name', 'country')
    list_filter = ('country',)
    search_fields = ('realm', 'name',)


admin.site.register(EduroamRealm, EduroamRealmAdmin)
