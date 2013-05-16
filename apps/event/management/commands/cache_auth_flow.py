# -*- coding: utf-8 -*-
__author__ = 'lundberg'

from django.core.management.base import BaseCommand, CommandError
from dateutil.tz import tzutc
from apps.event.views import get_auth_flow_data, get_protocol
from datetime import datetime, timedelta


class Command(BaseCommand):
    args = 'max_days min_days protocol'
    help = 'Runs the get_auth_flow_data so the result get cached.'

    def handle(self, *args, **options):
        try:
            default_max = int(args[0])
            default_min = int(args[1]) - 1
            protocol = get_protocol(args[2])
            today = datetime.now(tzutc())
            max_dt = today - timedelta(days=default_max)
            min_dt = today - timedelta(days=default_min)
            get_auth_flow_data(max_dt, min_dt, protocol)
        except ValueError:
            raise CommandError('Could not make sense of the max or min days.')
        except IndexError:
            raise CommandError('Please run the command as: cache_auth_flow max_days min_days protocol')