# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError
from dateutil.tz import tzutc
from flog.apps.event.models import EduroamEvent, OptimizedDailyEduroamEventAggregation
from datetime import datetime

__author__ = 'lundberg'


class Command(BaseCommand):
    args = 'start_date end_date'
    help = 'Aggregates Eduroam events per calling station ID, per day'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str)
        parser.add_argument('end_date', type=str)

    def handle(self, *args, **options):
        try:
            try:
                start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').replace(tzinfo=tzutc())
                end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').replace(tzinfo=tzutc())
                date_qs = EduroamEvent.objects.filter(ts__range=(start_date, end_date), successful=True).dates(
                    'ts', 'day', order='ASC')
                OptimizedDailyEduroamEventAggregation.objects.filter(date__range=(start_date, end_date)).delete()
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
"aggregate_eduroam_events_daily start_date end_date", date format is %Y-%m-%d')
