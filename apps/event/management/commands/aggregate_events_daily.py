# -*- coding: utf-8 -*-
__author__ = 'lundberg'

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.db.models import Count
from dateutil.tz import tzutc
from apps.event.models import Event, DailyEventAggregation
from apps.event.views import get_protocol
from datetime import datetime, timedelta


class Command(BaseCommand):
    args = 'yesterday|all'
    help = 'Aggregates events per protocol, per day'

    def handle(self, *args, **options):
        try:
            if args[0] == 'yesterday':
                today = datetime.now(tzutc()).replace(hour=0, minute=0, second=0, microsecond=0)
                yesterday = today - timedelta(days=1)
                qs = Event.objects.all().filter(ts__range=(yesterday, today)).extra(
                    {'date': 'date(ts)'}).values(
                        'date', 'origin__uri', 'rp__uri', 'protocol').annotate(num_events=Count('id'))
            elif args[0] == 'all':
                qs = Event.objects.all().extra({'date': 'date(ts)'}).values(
                    'date', 'origin__uri', 'rp__uri', 'protocol').annotate(num_events=Count('id'))

            for event_aggr in qs:
                de, created = DailyEventAggregation.objects.get_or_create(
                    date=event_aggr['date'],
                    origin_name=event_aggr['origin__uri'],
                    rp_name=event_aggr['rp__uri'],
                    protocol=event_aggr['protocol'],
                    defaults={'num_events': event_aggr['num_events']}
                )
                if not created:
                    de.num_events = event_aggr['num_events']
                    de.save()
        except ValueError:
            raise CommandError('Could not make sense of the max or min days.')
        except IndexError:
            raise CommandError('Please run the command as: \
"aggregate_events_daily yesterday" or "aggregate_events_daily all"')