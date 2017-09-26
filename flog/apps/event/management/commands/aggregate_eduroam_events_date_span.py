# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError
from dateutil.tz import tzutc
from flog.apps.event.models import EduroamEvent, DailyEduroamEventAggregation
from datetime import datetime, timedelta

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
                start_date = datetime.strptime(options['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(options['end_date'], '%Y-%m-%d')
                qs = EduroamEvent.objects.filter(ts__range=(start_date, end_date), successful=True).extra(
                    {'date': 'date(ts)'}).values('date', 'realm__realm', 'visited_institution__realm',
                                                 'visited_country__name', 'realm__country__name',
                                                 'calling_station_id')
            except ValueError:
                raise CommandError('%s is not an integer or "all".' % args[0])

            for event_aggr in qs.iterator():
                de, created = DailyEduroamEventAggregation.objects.get_or_create(
                    date=event_aggr['date'],
                    realm=event_aggr['realm__realm'],
                    visited_institution=event_aggr['visited_institution__realm'],
                    calling_station_id=event_aggr['calling_station_id'],
                    defaults={
                        'realm_country': event_aggr['realm__country__name'],
                        'visited_country': event_aggr['visited_country__name']
                    }
                )
                if not created:
                    de.realm_country = event_aggr['realm__country__name']
                    de.visited_country = event_aggr['visited_country__name']
                    de.save()

        except IndexError:
            raise CommandError('Please run the command as: \
"aggregate_eduroam_events_daily start_date end_date", date format is %Y-%m-%d')