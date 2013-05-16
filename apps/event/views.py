"""
Created on Apr 13, 2012

@author: leifj
"""

from dateutil import parser as dtparser
from django.utils.timezone import localtime
import json
import gc
from apps.event.models import Entity, Event
from django.shortcuts import get_object_or_404, render_to_response, RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models.aggregates import Count
from django.core.cache import cache
from django.db import connections, transaction

def get_protocol(protocol):
    protocols = {
        'Unknown': Event.Unknown,
        'WAYF': Event.WAYF,
        'Discovery': Event.Discovery,
        'SAML2': Event.SAML2,
    }
    if protocol in protocols:
        return protocols[protocol]
    return Event.SAML2

# Clear cache for sqlite (workaround)
def flush_cache():
    # This works as advertised on the memcached cache:
    cache.clear()
    # This manually purges the SQLite/postgres cache:
    cursor = connections['default'].cursor()
    cursor.execute('DELETE FROM flog_cache_table')
    transaction.commit_unless_managed(using='default')


def queryset_iterator(queryset, chunksize=100000):
    """
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 100000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    """
    pk = 0
    try:
        last_pk = queryset.order_by('-pk')[0].pk
    except IndexError:
        raise StopIteration
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


def entities(request):
    idp = Entity.objects.filter(is_idp=True).all()
    rp = Entity.objects.filter(is_rp=True).all()
    return render_to_response('event/list.html',
                              {'rps': rp.all(), 'idps': idp.all()},
                              context_instance=RequestContext(request))


@ensure_csrf_cookie
def by_rp(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'origin'
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        protocol = request.POST['protocol']
        data = cache.get('by-rp-%s-%s-%s-%s' % (pk, start_time.date(), end_time.date(), protocol), False)
        if not data:
            data = []
            d = Entity.objects.filter(origin_events__rp=entity,
                                      origin_events__ts__range=(start_time, end_time),
                                      origin_events__protocol=protocol)
            for e in d.annotate(count=Count('origin_events__id')).order_by('-count').iterator():
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('by-rp-%s-%s-%s-%s' % (pk, start_time.date(), end_time.date(), protocol),
                      data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 15)
        default_max = request.GET.get('max', 1)
        protocol = get_protocol(request.GET.get('protocol', 'SAML2'))
        try:
            threshold = float(request.GET.get('threshold', 0.05))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render_to_response('event/piechart.html',
                              {'entity': entity, 'cross_type': cross_type,
                               'threshold': threshold, 'default_min': default_min,
                               'default_max': default_max, 'protocol': protocol},
                              context_instance=RequestContext(request))


@ensure_csrf_cookie
def by_origin(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'rp'
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        protocol = request.POST['protocol']
        data = cache.get('by-origin-%s-%s-%s-%s' % (pk, start_time.date(), end_time.date(), protocol), False)
        if not data:
            data = []
            d = Entity.objects.filter(rp_events__origin=entity,
                                      rp_events__ts__range=(start_time, end_time),
                                      rp_events__protocol=protocol)
            for e in d.annotate(count=Count('rp_events__id'),).order_by('-count').iterator():
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('by-origin-%s-%s-%s-%s' % (pk, start_time.date(), end_time.date(), protocol),
                      data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 15)
        default_max = request.GET.get('max', 1)
        protocol = get_protocol(request.GET.get('protocol', 'SAML2'))
        try:
            threshold = float(request.GET.get('threshold', 0.05))
        except ValueError:
            return HttpResponse('Argument threshold not a decimal number.', content_type="text/html")
    return render_to_response('event/piechart.html',
                              {'entity': entity, 'cross_type': cross_type,
                               'threshold': threshold, 'default_min': default_min,
                               'default_max': default_max, 'protocol': protocol},
                              context_instance=RequestContext(request))


def get_auth_flow_data(start_time, end_time, protocol):
    data = cache.get('auth-flow-%s-%s-%s' % (start_time.date(), end_time.date(), protocol), False)
    if not data:
        qs = queryset_iterator(Event.objects.filter(protocol=protocol, ts__range=(start_time, end_time)))
        nodes = {}
        links = {}
        for e in qs:
            key = (e.rp_id, e.origin_id)
            if key in links:
                links[key]['value'] += 1
            else:
                links[key] = {
                    'source': key[0],
                    'target': key[1],
                    'value': 1
                }
                nodes[key[0]] = {'id': key[0], 'name': e.rp.uri}
                nodes[key[1]] = {'id': key[1], 'name': e.origin.uri}
        data = {
            'nodes': nodes.values(),
            'links': links.values()
        }
        cache.set('auth-flow-%s-%s-%s' % (start_time.date(), end_time.date(), protocol),
                  data, 60*60*24)  # 24h
    return data


@ensure_csrf_cookie
def auth_flow(request):
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        protocol = request.POST['protocol']
        data = get_auth_flow_data(start_time, end_time, protocol)
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        default_min = request.GET.get('min', 1)
        default_max = request.GET.get('max', 1)
        protocol = get_protocol(request.GET.get('protocol', 'SAML2'))
        try:
            threshold = int(request.GET.get('threshold', 50))
        except ValueError:
            return HttpResponse('Argument threshold not a number.', content_type="text/html")
    return render_to_response('event/sankey.html',
                              {'default_min': default_min, 'default_max': default_max,
                               "threshold": threshold, 'protocol': protocol},
                              context_instance=RequestContext(request))