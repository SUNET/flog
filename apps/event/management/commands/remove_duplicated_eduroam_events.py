# -*- coding: utf-8 -*-
__author__ = 'lundberg'

from django.core.management.base import BaseCommand, CommandError
from dateutil.tz import tzutc
from apps.event.models import EduroamEvent
from datetime import datetime, timedelta


class Command(BaseCommand):
    args = 'yesterday|all'
    help = 'Removes duplicated eduroam events'

    def handle(self, *args, **options):
        try:
            if args[0] == 'yesterday':
                today = datetime.now(tzutc()).replace(hour=0, minute=0, second=0, microsecond=0)
                yesterday = today - timedelta(days=1)
                events = EduroamEvent.objects.filter(ts__range=(yesterday, today))
            elif args[0] == 'all':
                events = EduroamEvent.objects.all()

            for event in events:
                qs = EduroamEvent.objects.filter(ts__lt=event.ts + timedelta(minutes=5),
                                                 ts__gt=event.ts - timedelta(minutes=5),
                                                 calling_station_id=event.calling_station_id).order_by('ts')
                if qs.count() > 1:
                    for dup in qs[1:]:
                        dup.delete()

        except IndexError:
            raise CommandError('Please run the command as: \
"remove_duplicated_eduroam_events yesterday" or "remove_duplicated_eduroam_events all"')