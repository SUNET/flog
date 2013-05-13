# -*- coding: utf-8 -*-
__author__ = 'lundberg'

from django.core.management.base import BaseCommand, CommandError
from apps.event.views import flush_cache


class Command(BaseCommand):
    help = 'Deletes the cache table from the db'

    def handle(self, *args, **options):
        try:
            flush_cache()
        except Exception as e:
            raise CommandError(e)