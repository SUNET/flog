# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError
from flog.apps.event.views import flush_cache

__author__ = 'lundberg'


class Command(BaseCommand):
    help = 'Deletes the cache table from the db'

    def handle(self, *args, **options):
        try:
            flush_cache()
        except Exception as e:
            raise CommandError(e)
