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
def by_rp(request, pk, default_min=15, default_max=1):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'origin'
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        data = cache.get('by-rp-%s-%s-%s' % (pk, start_time.date(), end_time.date()), False)
        if not data:
            data = []
            d = Entity.objects.filter(origin_events__rp=entity,
                                      origin_events__ts__range=(start_time, end_time))
            for e in d.annotate(count=Count('origin_events__id')).order_by('-count').iterator():
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('by-rp-%s-%s-%s' % (pk, start_time.date(), end_time.date()), data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render_to_response('event/piechart.html',
                              {'entity': entity, 'cross_type': cross_type,
                               'threshold': 0.05, "default_min": default_min,
                               "default_max": default_max},
                              context_instance=RequestContext(request))


@ensure_csrf_cookie
def by_origin(request, pk, default_min=15, default_max=1):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'rp'
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        data = cache.get('by-origin-%s-%s-%s' % (pk, start_time.date(), end_time.date()), False)
        if not data:
            data = []
            d = Entity.objects.filter(rp_events__origin=entity,
                                      rp_events__ts__range=(start_time, end_time))
            for e in d.annotate(count=Count('rp_events__id'),).order_by('-count').iterator():
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('by-origin-%s-%s-%s' % (pk, start_time.date(), end_time.date()), data, 60*60*24)  # 24h
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render_to_response('event/piechart.html',
                              {'entity': entity, 'cross_type': cross_type,
                               'threshold': 0.05, "default_min": default_min,
                               "default_max": default_max},
                              context_instance=RequestContext(request))


def get_auth_flow_data(start_time, end_time):
    data = cache.get('auth-flow-%s-%s' % (start_time.date(), end_time.date()), False)
    if not data:
        qs = queryset_iterator(Event.objects.filter(ts__range=(start_time, end_time)))
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
        cache.set('auth-flow-%s-%s' % (start_time.date(), end_time.date()), data, 60*60*24)  # 24h
    return data


@ensure_csrf_cookie
def auth_flow(request, default_min=1, default_max=1, value_threshold=50):
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        data = get_auth_flow_data(start_time, end_time)
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render_to_response('event/sankey.html',
                              {'default_min': default_min, 'default_max': default_max,
                               "value_threshold": value_threshold},
                              context_instance=RequestContext(request))