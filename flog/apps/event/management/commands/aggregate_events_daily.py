# -*- coding: utf-8 -*-
__author__ = 'lundberg'

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from dateutil.tz import tzutc
from apps.event.models import Event, DailyEventAggregation
from datetime import datetime, timedelta


class Command(BaseCommand):
    args = 'n|all'
    help = 'Aggregates events per protocol, per day'

    def handle(self, *args, **options):
        try:
            if args[0] == 'all':
                qs = Event.objects.all().extra({'date': 'date(ts)'}).values(
                    'date', 'origin__uri', 'rp__uri', 'protocol').annotate(num_events=Count('id'))
            else:
                try:
                    days = int(args[0])
                    today = datetime.now(tzutc()).replace(hour=0, minute=0, second=0, microsecond=0)
                    n_days_before = today - timedelta(days=days)
                    qs = Event.objects.filter(ts__range=(n_days_before, today)).extra({'date': 'date(ts)'}).values(
                        'date', 'origin__uri', 'rp__uri', 'protocol').annotate(num_events=Count('id'))
                except ValueError:
                    raise CommandError('%s is not an integer or "all".' % args[0])

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
        except IndexError:
            raise CommandError('Please run the command as: \
"aggregate_events_daily [n days]" or "aggregate_events_daily all"')