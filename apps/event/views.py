"""
Created on Apr 13, 2012

@author: leifj
"""

from dateutil import parser as dtparser
from django.utils.timezone import localtime
import json
from apps.event.models import Entity, Event
from django.shortcuts import get_object_or_404, render_to_response, RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models.aggregates import Count
from django.core.cache import cache


@ensure_csrf_cookie
def by_rp(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'origin'
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        data = cache.get('by-rp-%s-%s' % (start_time.date(), end_time.date()), False)
        if not data:
            data = []
            d = Entity.objects.filter(origin_events__rp=entity,
                                      origin_events__ts__range=(start_time, end_time))
            for e in d.annotate(count=Count('origin_events__id')).order_by('-count'):
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('by-rp-%s-%s' % (start_time.date(), end_time.date()), data)
        return HttpResponse(json.dumps(data), content_type="application/json")

    return render_to_response('event/piechart.html',
                              {'entity': entity, 'cross_type': cross_type, 'threshold': 0.05},
                              context_instance=RequestContext(request))


@ensure_csrf_cookie
def by_origin(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'rp'
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        data = cache.get('by-origin-%s-%s' % (start_time.date(), end_time.date()), False)
        if not data:
            data = []
            d = Entity.objects.filter(rp_events__origin=entity,
                                      rp_events__ts__range=(start_time, end_time))
            for e in d.annotate(count=Count('rp_events__id'),).order_by('-count'):
                data.append({'label': str(e), 'data': e.count, 'id': e.id})
            cache.set('by-origin-%s-%s' % (start_time.date(), end_time.date()), data)
        return HttpResponse(json.dumps(data), content_type="application/json")

    return render_to_response('event/piechart.html',
                              {'entity': entity, 'cross_type': cross_type, 'threshold': 0.05},
                              context_instance=RequestContext(request))

@ensure_csrf_cookie
def auth_flow(request):
    if request.POST:
        start_time = localtime(dtparser.parse(request.POST['start']))
        end_time = localtime(dtparser.parse(request.POST['end']))
        data = cache.get('auth-flow-%s-%s' % (start_time.date(), end_time.date()), False)
        if not data:
            d = Event.objects.filter(ts__range=(start_time, end_time)).values('origin__id', 'origin__uri',
                                                                              'rp__id', 'rp__uri')
            nodes = {}
            links = {}
            for e in d:
                key = (e['rp__id'], e['origin__id'])
                if key in links:
                    links[key]['value'] += 1
                else:
                    links[key] = {
                        'source': key[0],
                        'target': key[1],
                        'value': 1
                    }
                    nodes[key[0]] = {'id': key[0], 'name': e['rp__uri']}
                    nodes[key[1]] = {'id': key[1], 'name': e['origin__uri']}
            data = {
                'nodes': nodes.values(),
                'links': links.values()
            }
            cache.set('auth-flow-%s-%s' % (start_time.date(), end_time.date()), data)
        return HttpResponse(json.dumps(data), content_type="application/json")
    return render_to_response('event/sankey.html', {'width': 940, 'height': 1500},
                              context_instance=RequestContext(request))


def entities(request):
    idp = Entity.objects.filter(is_idp=True).all()
    rp = Entity.objects.filter(is_rp=True).all()
    return render_to_response('event/list.html',
                              {'rps':rp.all(),'idps':idp.all()},
                              context_instance=RequestContext(request))