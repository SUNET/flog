"""
Created on Apr 13, 2012

@author: leifj
"""

from django.db import models
from django.db.models.fields import DateTimeField, URLField, SmallIntegerField,\
    CharField, BooleanField
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
        return "%s;%s;%s;%s;%s" % (self.ts, self.protocol, self.principal,
                                   self.origin, self.rp)


def _add_event(ts, origin, rp, protocol, principal=None):
    event, created = Event.objects.get_or_create(ts=ts, origin=origin, rp=rp,
                                                 protocol=protocol, principal=principal)
    if created:
        return 1
    else:
        return 0


def add_event(ts, origin_uri, rp_uri, protocol, principal=None):
    origin, created = Entity.objects.get_or_create(uri=origin_uri)
    if not origin.is_idp:
        origin.is_idp = True
        origin.save()
    
    rp, created = Entity.objects.get_or_create(uri=rp_uri)
    if not rp.is_rp:
        rp.is_rp = True
        rp.save()
        
    return _add_event(ts, origin, rp, protocol, principal)


def import_events(lines):
    cache = {}
    lst = []
    for line in lines.split('\n'):
        if len(lst) > 100:
            Event.objects.bulk_create(lst)
            lst = []
            
        try:
            logging.debug(line)
            (ts, protocol, rp_uri, origin_uri, principal) = line.split(';')
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
                
            lst.append(Event(ts=ts, origin=origin, rp=rp, protocol=p, principal=principal))
        except Exception, exc:
            logging.error(exc)
    
    if len(lst) > 0:
        Event.objects.bulk_create(lst)


def import_event(line, cache={}):
    (ts, protocol, rp_uri, origin_uri, principal) = line.split(';')
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
    
    if not origin_uri in cache:
        origin, created = Entity.objects.get_or_create(uri=origin_uri)
        if not origin.is_idp:
            origin.is_idp = True
            origin.save()
        cache[origin_uri] = origin
        
    return _add_event(ts,cache[origin_uri],cache[rp_uri],p,principal)