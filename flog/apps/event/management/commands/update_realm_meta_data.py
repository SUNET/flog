# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
from flog.apps.event.models import EduroamRealm, Country
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from xml.etree.ElementTree import iterparse

__author__ = 'lundberg'


class Command(BaseCommand):
    can_import_settings = True
    help = 'Parses an xml meta data file and updates the existing realms.'

    def handle(self, *args, **options):
        # Start by matching realms with unknown country to already existing countries
        default_country, created = Country.objects.get_or_create(country_code='0')
        for realm in default_country.country_realms.all():
            country_code = realm.realm.split('.')[-1]
            try:
                country = Country.objects.get(country_code=country_code)
                realm.country = country
                realm.save()
            except Country.DoesNotExist:
                pass
        try:
            from django.conf import settings
            meta_data = settings.EDUROAM_META_DATA
            with open(meta_data) as source:
                context = iter(iterparse(source, events=("start", "end")))
                # get the root element
                for event, elem in context:
                    if event == "end" and elem.tag == "institution":
                        inst_realm = elem.findtext('inst_realm')
                        country_code = elem.findtext('country')
                        org_name = elem.findtext('org_name')
                        if inst_realm and country_code:
                            country_code = country_code.lower()
                            inst_realm = inst_realm.lower()
                            try:
                                country, created = Country.objects.get_or_create(country_code=country_code)
                                realm = EduroamRealm.objects.get(realm=inst_realm)
                                realm.name = org_name
                                realm.country = country
                                realm.save()
                            except ObjectDoesNotExist:
                                pass
        except ImportError:
            raise CommandError('Could not import settings.py.')
        except IOError as e:
            logging.error(e)
            raise CommandError('Could not open meta data file: %s' % meta_data)
        except DatabaseError as e:
            # Probably a country code that is not a country code.
            logging.error(e)
