# -*- coding: utf-8 -*-
__author__ = 'lundberg'

from django.core.management.base import BaseCommand, CommandError
from dateutil.tz import tzutc
from apps.event.models import EduroamEvent
from datetime import datetime, timedelta

#
# Duplicated is apparently a event with same csi with in 5 minutes of each other.
#


class Command(BaseCommand):
    args = 'n|all'
    help = 'Removes duplicated eduroam events'

    def handle(self, *args, **options):
        try:
            if args[0] == 'all':
                successful_events = EduroamEvent.objects.filter(successful=True)
                fail_events = EduroamEvent.objects.filter(successful=False)
            else:
                try:
                    days = int(args[0])
                    today = datetime.now(tzutc()).replace(hour=0, minute=0, second=0, microsecond=0)
                    n_days_before = today - timedelta(days=days)
                    successful_events = EduroamEvent.objects.filter(ts__range=(n_days_before, today), successful=True)
                    fail_events = EduroamEvent.objects.filter(ts__range=(n_days_before, today), successful=False)
                except ValueError:
                    raise CommandError('%s is not an integer or "all".' % args[0])

            for event in successful_events.iterator():
                qs = EduroamEvent.objects.filter(ts__lt=event.ts + timedelta(minutes=5),
                                                 ts__gt=event.ts - timedelta(minutes=5),
                                                 calling_station_id=event.calling_station_id).order_by('ts')
                if qs.count() > 1:
                    for dup in qs[1:]:
                        dup.delete()

            for event in fail_events.iterator():
                qs = EduroamEvent.objects.filter(ts__lt=event.ts + timedelta(minutes=5),
                                                 ts__gt=event.ts - timedelta(minutes=5),
                                                 calling_station_id=event.calling_station_id).order_by('ts')
                if qs.count() > 1:
                    for dup in qs[1:]:
                        dup.delete()

        except IndexError:
            raise CommandError('Please run the command as: \
"remove_duplicated_eduroam_events [n days]" or "remove_duplicated_eduroam_events all"')