"""
Created on Apr 13, 2012

@author: leifj
"""

from django.db import models
from django.db.models.fields import DateTimeField, DateField, URLField, SmallIntegerField,\
    CharField, BooleanField, BigIntegerField
from django.db.models.fields.related import ForeignKey
from django.core.cache import cache
from django.utils import dateparse
import logging

logger = logging.getLogger(__name__)


class Entity(models.Model):

    class Meta:
        ordering = ['uri']

    uri = URLField(db_index=True, unique=True)
    is_idp = BooleanField(default=False)
    is_rp = BooleanField(default=False)
    
    def __str__(self):
        return self.uri


class Event(models.Model):
    ts = DateTimeField(db_index=True)
    origin = ForeignKey(Entity, related_name='origin_events', on_delete=models.CASCADE)
    rp = ForeignKey(Entity, related_name='rp_events', on_delete=models.CASCADE)
    protocol = SmallIntegerField(choices=((0, 'Unknown'),
                                          (1, 'WAYF'),
                                          (2, 'Discovery'),
                                          (3, 'SAML2')))
    principal = CharField(max_length=128, null=True, blank=True)
    
    Unknown = 0
    WAYF = 1
    Discovery = 2
    SAML2 = 3
    
    def __str__(self):
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

    def __str__(self):
        return '%s %dx %s -[%d]-> %s' % (self.date, self.num_events, self.rp_name, self.protocol, self.origin_name)


class Country(models.Model):

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'countries'

    country_code = CharField(max_length=3, unique=True)
    name = CharField(max_length=256, blank=True, default='Unknown')

    def __str__(self):
        return '%s (%s)' % (self.name, self.country_code)


def get_default_country():
    country, created = Country.objects.get_or_create(country_code='0', name='Unknown')
    return country


class EduroamRealm(models.Model):

    class Meta:
        ordering = ['realm']

    realm = CharField(max_length=128, unique=True)
    name = CharField(max_length=256, blank=True)
    country = ForeignKey(Country, related_name='country_realms',
                         blank=True, null=True, on_delete=models.SET_NULL,
                         default=get_default_country)

    def __str__(self):
        return self.realm


class EduroamEvent(models.Model):
    ts = DateTimeField(db_index=True)
    version = CharField(max_length=10)
    realm = ForeignKey(EduroamRealm, related_name='realm_events', on_delete=models.CASCADE)
    visited_country = ForeignKey(Country, related_name='country_events', on_delete=models.CASCADE)
    visited_institution = ForeignKey(EduroamRealm, related_name='institution_events',
                                     blank=True, null=True, on_delete=models.SET_NULL)
    calling_station_id = CharField(max_length=128)
    successful = BooleanField(db_index=True)

    def __str__(self):
        return '%s;%s;%s;%s;%s;%s;%s' % (self.ts, self.version, self.realm, self.visited_country,
                                         self.visited_institution, self.calling_station_id, self.successful)


class DailyEduroamEventAggregation(models.Model):

    class Meta:
        unique_together = ('date', 'realm', 'visited_institution', 'calling_station_id')

    date = DateField(db_index=True)
    realm = CharField(max_length=200)
    visited_institution = CharField(max_length=200)
    calling_station_id = CharField(max_length=128)
    realm_country = CharField(max_length=200)
    visited_country = CharField(max_length=200)

    def __str__(self):
        return '%s %s --> %s' % (self.date, self.realm, self.visited_institution)


class OptimizedDailyEduroamEventAggregation(models.Model):

    class Meta:
        unique_together = ('date', 'realm', 'visited_institution')

    date = DateField(db_index=True)
    realm = ForeignKey(EduroamRealm, related_name='realm_daily_events', on_delete=models.CASCADE)
    visited_institution = ForeignKey(EduroamRealm, related_name='institution_daily_events', on_delete=models.CASCADE)
    calling_station_id_count = BigIntegerField(default=0)

    def __str__(self):
        return '%s %s -[%s]-> %s' % (self.date, self.realm, self.calling_station_id_count, self.visited_institution)


def import_websso_events(event, batch):
    try:
        logger.debug(event)
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

        rp = cache.get(rp_uri)
        if not rp:
            rp, created = Entity.objects.get_or_create(uri=rp_uri)
            if not rp.is_rp:
                rp.is_rp = True
                rp.save()
            cache.set(rp_uri, rp)

        origin = cache.get(origin_uri)
        if not origin:
            origin, created = Entity.objects.get_or_create(uri=origin_uri)
            if not origin.is_idp:
                origin.is_idp = True
                origin.save()
            cache.set(origin_uri, origin)

        batch.append(Event(ts=ts, origin=origin, rp=rp, protocol=p, principal=principal))
    except Exception as exc:
        logger.error(exc)
    return batch


def import_eduroam_events(event, batch):
    try:
        logger.debug(event)
        (ts, eduroam, version, event_realm, visited_country, visited_institution, calling_station_id, result) = event

        # Disregard failed authentications
        success = True
        if result.lower() != 'ok':
            return batch

        # Check if any event with identical calling_station_id and visited_institution
        # has been seen in the last 5 minutes. If so, disregard that event
        csi_last_event = cache.get(calling_station_id)
        if csi_last_event:
            # A cache hit should filter duplicate events in normal operation
            # but even if we hit the cache we need to check the timestamps
            # due to batch inserting logs after downtime.
            last_dt = dateparse.parse_datetime(csi_last_event)
            current_dt = dateparse.parse_datetime(ts)
            diff = last_dt - current_dt
            if int(abs(diff.total_seconds())) <= 300:
                return batch

        visited_institution = visited_institution.lower()
        visited_institution = visited_institution.lstrip('1')  # Realm as Operator-Name indicated by a leading 1
        visited_institution = visited_institution.lstrip('2')  # Realm as Mobile Country Code indicated by a leading 2
        visited_realm = cache.get(visited_institution)
        if not visited_realm:
            visited_realm, created = EduroamRealm.objects.get_or_create(realm=visited_institution)
            cache.set(visited_institution, visited_realm)

        event_realm = event_realm.lower()
        realm = cache.get(event_realm)
        if not realm:
            realm, created = EduroamRealm.objects.get_or_create(realm=event_realm)
            cache.set(event_realm, realm)

        visited_country = visited_country.lower()
        country = cache.get(visited_country)
        if not country:
            country, created = Country.objects.get_or_create(country_code=visited_country)
            cache.set(visited_country, country)

        batch.append(EduroamEvent(ts=ts, version=version, realm=realm, visited_country=country,
                                  visited_institution=visited_realm, calling_station_id=calling_station_id,
                                  successful=success))
        cache.set(calling_station_id, ts, 300)
    except Exception as exc:
        logger.error(exc)
    return batch


def import_events(lines):
    websso_batch, eduroam_batch = [], []
    for line in lines.split('\n'):
        # Batch create
        if len(websso_batch) > 100:
            objs = Event.objects.bulk_create(websso_batch)
            logger.debug('websso bulk create > 100 lines')
            logger.debug(objs)
            websso_batch = []
        if len(eduroam_batch) > 100:
            objs = EduroamEvent.objects.bulk_create(eduroam_batch)
            logger.debug('eduroam bulk create > 100 lines')
            logger.debug(objs)
            eduroam_batch = []
        try:
            event = line.split(';')
            if event[1] == 'eduroam':
                eduroam_batch = import_eduroam_events(event, eduroam_batch)
            else:
                websso_batch = import_websso_events(event, websso_batch)
        except (ValueError, IndexError) as exc:
            logger.error(exc)
    # Batch create
    if len(websso_batch) > 0:
        objs = Event.objects.bulk_create(websso_batch)
        logger.debug('websso bulk create end of request')
        logger.debug(objs)
    if len(eduroam_batch) > 0:
        objs = EduroamEvent.objects.bulk_create(eduroam_batch)
        logger.debug('eduroam bulk create end of request')
        logger.debug(objs)
