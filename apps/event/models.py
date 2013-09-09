"""
Created on Apr 13, 2012

@author: leifj
"""

from django.db import models
from django.db.models.fields import DateTimeField, DateField, URLField, SmallIntegerField,\
    CharField, BooleanField, BigIntegerField
from django.db.models.fields.related import ForeignKey
import logging


class Entity(models.Model):

    class Meta:
        ordering = ['uri']

    uri = URLField(db_index=True, unique=True)
    is_idp = BooleanField(default=False)
    is_rp = BooleanField(default=False)
    
    def __unicode__(self):
        return self.uri


class Event(models.Model):
    ts = DateTimeField(db_index=True)
    origin = ForeignKey(Entity, related_name='origin_events')
    rp = ForeignKey(Entity, related_name='rp_events')
    protocol = SmallIntegerField(choices=((0, 'Unknown'),
                                          (1, 'WAYF'),
                                          (2, 'Discovery'),
                                          (3, 'SAML2')))
    principal = CharField(max_length=128, null=True, blank=True)
    
    Unknown = 0
    WAYF = 1
    Discovery = 2
    SAML2 = 3
    
    def __unicode__(self):
        return '%s;%s;%s;%s;%s' % (self.ts, self.protocol, self.principal,
                                   self.origin, self.rp)


class DailyEventAggregation(models.Model):

    class Meta:
        unique_together = ('date', 'origin_name', 'rp_name', 'protocol')

    date = DateField(db_index=True)
    origin_name = CharField(max_length=200)
    rp_name = CharField(max_length=200)
    protocol = SmallIntegerField(choices=((0, 'Unknown'),
                                          (1, 'WAYF'),
                                          (2, 'Discovery'),
                                          (3, 'SAML2')))
    num_events = BigIntegerField()

    def __unicode__(self):
        return '%s %dx %s -[%d]-> %s' % (self.date, self.num_events, self.rp_name, self.protocol, self.origin_name)


class Country(models.Model):

    class Meta:
        ordering = ['country_code']

    country_code = CharField(max_length=3, unique=True)
    name = CharField(max_length=256, blank=True, default='Unknown')

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.country_code)


class EduroamRealm(models.Model):

    class Meta:
        ordering = ['realm']

    realm = CharField(max_length=128, unique=True)
    name = CharField(max_length=256, blank=True)
    country = ForeignKey(Country, related_name='country_realms',
                         blank=True, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.realm


class EduroamEvent(models.Model):
    ts = DateTimeField(db_index=True)
    version = CharField(max_length=10)
    realm = ForeignKey(EduroamRealm, related_name='realm_events')
    visited_country = ForeignKey(Country, related_name='country_events')
    visited_institution = ForeignKey(EduroamRealm, related_name='institution_events',
                                     blank=True, null=True, on_delete=models.SET_NULL)
    calling_station_id = CharField(max_length=128)
    successful = BooleanField()

    def __unicode__(self):
        return '%s;%s;%s;%s;%s;%s;%s' % (self.ts, self.version, self.realm, self.visited_country,
                                         self.visited_institution, self.calling_station_id, self.successful)


def import_websso_events(event, cache, batch):
    try:
        logging.debug(event)
        (ts, protocol, rp_uri, origin_uri, principal) = event
        p = Event.Unknown
        try:
            p = int(protocol)
        except ValueError:
            pass
        if protocol == 'D':
            p = Event.Discovery
        elif protocol == 'W':
            p = Event.WAYF

        if not rp_uri in cache:
            rp, created = Entity.objects.get_or_create(uri=rp_uri)
            if not rp.is_rp:
                rp.is_rp = True
                rp.save()
            cache[rp_uri] = rp
        rp = cache[rp_uri]

        if not origin_uri in cache:
            origin, created = Entity.objects.get_or_create(uri=origin_uri)
            if not origin.is_idp:
                origin.is_idp = True
                origin.save()
            cache[origin_uri] = origin
        origin = cache[origin_uri]

        batch.append(Event(ts=ts, origin=origin, rp=rp, protocol=p, principal=principal))
    except Exception, exc:
        logging.error(exc)
    return cache, batch


def import_eduroam_events(event, cache, batch):
    try:
        logging.debug(event)
        (ts, eduroam, version, event_realm, visited_country, visited_institution, calling_station_id, result) = event
        success = False
        if result.lower() == 'ok':
            success = True

        event_realm = event_realm.lower()
        if not event_realm in cache:
            realm, created = EduroamRealm.objects.get_or_create(realm=event_realm)
            cache[event_realm] = realm
        realm = cache[event_realm]

        visited_country = visited_country.lower()
        if not visited_country in cache:
            country, created = Country.objects.get_or_create(country_code=visited_country)
            cache[visited_country] = country
        country = cache[visited_country]

        visited_institution = visited_institution.lower().lstrip('1')  # Realm as Operator-Name indicated by a leading 1
        if not visited_institution in cache:
            visited_realm, created = EduroamRealm.objects.get_or_create(realm=visited_institution)
            cache[visited_institution] = visited_realm
        visited_realm = cache[visited_institution]

        batch.append(EduroamEvent(ts=ts, version=version, realm=realm, visited_country=country,
                                  visited_institution=visited_realm, calling_station_id=calling_station_id,
                                  successful=success))
    except Exception, exc:
        logging.error(exc)
    return cache, batch


def import_events(lines):
    websso_cache, eduroam_cache = {}, {}
    websso_batch, eduroam_batch = [], []
    for line in lines.split('\n'):
        # Batch create
        if len(websso_batch) > 100:
            Event.objects.bulk_create(websso_batch)
            websso_batch = []
        if len(eduroam_batch) > 100:
            EduroamEvent.objects.bulk_create(eduroam_batch)
            eduroam_batch = []
        try:
            event = line.split(';')
            if event[1] == 'eduroam':
                eduroam_cache, eduroam_batch = import_eduroam_events(event, eduroam_cache, eduroam_batch)
            else:
                websso_cache, websso_batch = import_websso_events(event, websso_cache, websso_batch)
        except (ValueError, IndexError) as exc:
            logging.error(exc)
    # Batch create
    if len(websso_batch) > 0:
        Event.objects.bulk_create(websso_batch)
    if len(eduroam_batch) > 0:
        EduroamEvent.objects.bulk_create(eduroam_batch)
