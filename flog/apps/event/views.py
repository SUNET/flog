"""
Created on Apr 13, 2012

@author: leifj
"""
from datetime import datetime, timedelta
import json
from flog.apps.event.models import Entity, Event
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models.aggregates import Count
from flog.multiresponse import respond_to, json_response


def by_rp(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'origin'
    if request.POST:
        start_date = datetime.strptime(request.POST['start'][:28], "%a %b %d %Y %H:%M:%S %Z")
        end_date = datetime.strptime(request.POST['end'][:28], "%a %b %d %Y %H:%M:%S %Z")
        d = Entity.objects.filter(origin_events__rp=entity,
                                  origin_events__ts__gt=start_date,
                                  origin_events__ts__lt=end_date)
        data = []
        for e in d.annotate(count=Count('origin_events__id')).order_by('-count'):
            data.append({'label': str(e), 'data': e.count, 'id': e.id})
        return HttpResponse(json.dumps(data), content_type="application/json")

    return respond_to(request, {'text/html': 'apps/event/piechart.html'},
                      {'entity': entity, 'cross_type': cross_type, 'threshold': 0.05})


def by_origin(request, pk):
    entity = get_object_or_404(Entity, pk=pk)
    cross_type = 'rp'
    if request.POST:
        start_date = datetime.strptime(request.POST['start'][:28], "%a %b %d %Y %H:%M:%S %Z")
        end_date = datetime.strptime(request.POST['end'][:28], "%a %b %d %Y %H:%M:%S %Z")
        d = Entity.objects.filter(rp_events__origin=entity,
                                  rp_events__ts__gt=start_date,
                                  rp_events__ts__lt=end_date)
        data = []
        for e in d.annotate(count=Count('rp_events__id'),).order_by('-count'):
            data.append({'label': str(e), 'data': e.count, 'id': e.id})
        return HttpResponse(json.dumps(data), content_type="application/json")

    return respond_to(request, {'text/html': 'apps/event/piechart.html'},
                      {'entity': entity, 'cross_type': cross_type, 'threshold': 0.05})


def entities(request):
    idp = Entity.objects.filter(is_idp=True).all()
    rp = Entity.objects.filter(is_rp=True).all()
    return respond_to(request,{'text/html': 'apps/event/list.html'},{'rps':rp.all(),'idps':idp.all()})