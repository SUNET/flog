# -*- coding: utf-8 -*-
__author__ = 'lundberg'

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from dateutil.tz import tzutc
from apps.event.models import EduroamEvent, DailyEduroamEventAggregation
from datetime import datetime, timedelta


class Command(BaseCommand):
    args = 'yesterday|all'
    help = 'Aggregates Eduroam events per calling station ID, per day'

    def handle(self, *args, **options):
        try:
            if args[0] == 'yesterday':
                today = datetime.now(tzutc()).replace(hour=0, minute=0, second=0, microsecond=0)
                yesterday = today - timedelta(days=1)
                qs = EduroamEvent.objects.filter(ts__range=(yesterday, today)).extra(
                    {'date': 'date(ts)'}).values('date', 'realm__realm', 'visited_institution__realm',
                                                 'visited_country__name', 'realm__country__name', 'calling_station_id')
            elif args[0] == 'all':
                qs = EduroamEvent.objects.all().extra({'date': 'date(ts)'}).values(
                    'date', 'realm__realm', 'visited_institution__realm', 'visited_country__name',
                    'realm__country__name', 'calling_station_id')

            for event_aggr in qs:
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
"aggregate_eduroam_events_daily yesterday" or "aggregate_eduroam_events_daily all"')