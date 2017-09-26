# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError
from dateutil.tz import tzutc
from flog.apps.event.views import get_auth_flow_data, get_protocol
from datetime import datetime, timedelta

__author__ = 'lundberg'


class Command(BaseCommand):
    args = 'max_days min_days protocol'
    help = 'Runs the get_auth_flow_data so the result get cached. Example: "7 1 SAML2" caches last weeks data.'

    def add_arguments(self, parser):
        parser.add_argument('max_days', type=int)
        parser.add_argument('min_days', type=int)
        parser.add_argument('protocol', type=str)

    def handle(self, *args, **options):
        try:
            default_max = int(options['max_days'])
            default_min = int(options['min_days']) - 1
            protocol = get_protocol(options['protocol'])
            today = datetime.now(tzutc()).replace(hour=0, minute=0, second=0, microsecond=0)
            max_dt = today - timedelta(days=default_max)
            min_dt = today - timedelta(days=default_min)
            get_auth_flow_data(max_dt, min_dt, protocol)
        except ValueError:
            raise CommandError('Could not make sense of the max or min days.')
        except IndexError:
            raise CommandError('Please run the command as: cache_auth_flow max_days min_days protocol')