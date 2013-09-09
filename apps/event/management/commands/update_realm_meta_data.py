# -*- coding: utf-8 -*-
__author__ = 'lundberg'

import logging
from apps.event.models import EduroamRealm, Country
from django.core.management.base import NoArgsCommand, CommandError
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from xml.etree.ElementTree import iterparse


class Command(NoArgsCommand):
    can_import_settings = True
    help = 'Parses an xml meta data file and updates the existing realms.'

    def handle_noargs(self, **options):
        try:
            from django.conf import settings
            meta_data = settings.EDUROAM_META_DATA
            with open(meta_data) as source:
                context = iter(iterparse(source, events=("start", "end")))
                # get the root element
                event, root = context.next()
                for event, elem in context:
                    if event == "end" and elem.tag == "institution":
                        inst_realm = elem.findtext('inst_realm')
                        country_code = elem.findtext('country')
                        org_name = elem.findtext('org_name')
                        try:
                            country, created = Country.objects.get_or_create(country_code=country_code)
                            realm = EduroamRealm.objects.get(realm=inst_realm)
                            realm.name = org_name
                            realm.country = country
                            realm.save()
                        except ObjectDoesNotExist:
                            pass
                    root.clear()
        except ImportError:
            raise CommandError('Could not import settings.py.')
        except IOError:
            raise CommandError('Could not open meta data file: %s' % meta_data)
        except DatabaseError as e:
            # Probably a country code that is not a country code.
            logging.error(e)