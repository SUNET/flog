# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError
from django.db.models.aggregates import Count
from dateutil.tz import tzutc
from flog.apps.event.models import DailyEduroamEventAggregation, OptimizedDailyEduroamEventAggregation, EduroamRealm
from datetime import datetime

__author__ = 'lundberg'


class Command(BaseCommand):
    args = 'start_date end_date'
    help = 'Aggregates old aggregated Eduroam events to new aggregated daily events'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true')
        parser.add_argument('start_date', type=str)
        parser.add_argument('end_date', type=str)

    def handle(self, *args, **options):
        try:
            if options['all']:
                date_qs = DailyEduroamEventAggregation.objects.dates('date', 'day', order='ASC')
                OptimizedDailyEduroamEventAggregation.objects.all().delete()
            else:
                try:
                    start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').replace(tzinfo=tzutc())
                    end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').replace(tzinfo=tzutc())
                    date_qs = DailyEduroamEventAggregation.objects.filter(date__range=(start_date, end_date)).dates(
                        'date', 'day', order='ASC')
                    OptimizedDailyEduroamEventAggregation.objects.filter(date__range=(start_date, end_date)).delete()
                except ValueError:
                    raise CommandError('%s is not a data in the form YY-MM-DD' % args[0])
            realm_qs = EduroamRealm.objects.all()
            realm_map = dict(realm_qs.values_list('realm', 'id'))
            for date in date_qs:
                qs = DailyEduroamEventAggregation.objects.filter(date=date).values(
                    'realm', 'visited_institution').order_by().annotate(Count('calling_station_id'))
                for event in qs:
                    aggregated_event, created = OptimizedDailyEduroamEventAggregation.objects.get_or_create(
                        date=date,
                        realm=realm_qs.get(id=realm_map[event['realm']]),
                        visited_institution=realm_qs.get(id=realm_map[event['visited_institution']]),
                        calling_station_id_count=event['calling_station_id__count']
                    )

        except IndexError:
            raise CommandError('Please run the command as: \
"aggregate_eduroam_events_daily start_date end_date", date format is %Y-%m-%d')
