# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError
from dateutil.tz import tzutc
from flog.apps.event.models import EduroamEvent, OptimizedDailyEduroamEventAggregation
from datetime import datetime, timedelta

__author__ = 'lundberg'


class Command(BaseCommand):
    args = 'n|all'
    help = 'Aggregates Eduroam events per calling station ID, per day'

    def add_arguments(self, parser):
        parser.add_argument('n_or_all', type=str)

    def handle(self, *args, **options):
        try:
            if options['n_or_all'] == 'all':
                date_qs = EduroamEvent.objects.filter(successful=True).dates('ts', 'day', order='ASC')
                OptimizedDailyEduroamEventAggregation.objects.all().delete()
            else:
                try:
                    days = int(options['n_or_all'])
                    today = datetime.now(tzutc()).replace(hour=0, minute=0, second=0, microsecond=0)
                    n_days_before = today - timedelta(days=days)
                    date_qs = EduroamEvent.objects.filter(ts__range=(n_days_before, today), successful=True).dates(
                        'ts', 'day', order='ASC')
                    OptimizedDailyEduroamEventAggregation.objects.filter(date__range=(n_days_before, today)).delete()
                except ValueError:
                    raise CommandError('%s is not an integer or "all".' % args[0])

            for date in date_qs:
                qs = EduroamEvent.objects.filter(ts__date=date, successful=True).distinct(
                    'realm', 'visited_institution', 'calling_station_id')
                for event in qs.iterator():
                    aggregated_event, created = OptimizedDailyEduroamEventAggregation.objects.get_or_create(
                        date=date,
                        realm=event.realm,
                        visited_institution=event.visited_institution,
                        defaults={'calling_station_id_count': 1}
                    )
                    if not created:
                        aggregated_event.calling_station_id_count += 1
                        aggregated_event.save()
        except IndexError:
            raise CommandError('Please run the command as: \
"aggregate_eduroam_events_daily [n days]" or "aggregate_eduroam_events_daily all"')
