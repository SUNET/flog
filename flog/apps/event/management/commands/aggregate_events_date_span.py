# -*- coding: utf-8 -*-
__author__ = 'lundberg'

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from dateutil.tz import tzutc
from apps.event.models import Event, DailyEventAggregation
from datetime import datetime, timedelta


class Command(BaseCommand):
    args = 'start_date end_date'
    help = 'Aggregates events per protocol, per day.'

    def handle(self, *args, **options):
        try:

            try:
                start_date_string = args[0]
                end_date_string = args[1]
                start_date = datetime.strptime(start_date_string, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_string, '%Y-%m-%d')
                qs = Event.objects.filter(ts__range=(start_date, end_date)).extra({'date': 'date(ts)'}).values(
                    'date', 'origin__uri', 'rp__uri', 'protocol').annotate(num_events=Count('id'))
            except ValueError:
                raise CommandError('%s is not an integer or "all".' % args[0])

            for event_aggr in qs.iterator():
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
"aggregate_events_daily start_date end_date", date format is %Y-%m-%d')