'''
Created on Apr 13, 2012

@author: leifj
'''
from flog.apps.event.models import Entity, Event
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from flog.multiresponse import respond_to    


def by_rp(request,pk):
    entity = get_object_or_404(Entity,pk=pk)
    cross_type = 'origin'
    
    h = Entity.objects.filter(origin_events__rp=entity).annotate(count=Count('origin_events__id')).order_by('-count')
    return respond_to(request, {'text/html': 'apps/event/histogram.html'}, 
                      {'entity':entity, 'histogram': h,'cross_type': cross_type,'threshold': 0.05})

def by_origin(request,pk):
    entity = get_object_or_404(Entity,pk=pk)
    cross_type = 'rp'
    
    h = Entity.objects.filter(rp_events__origin=entity).annotate(count=Count('rp_events__id')).order_by('-count')
    return respond_to(request, {'text/html': 'apps/event/histogram.html'}, 
                      {'entity':entity, 'histogram': h,'cross_type': cross_type,'threshold': 0.05})
    
def entities(request):
    idp = Entity.objects.filter(is_idp=True).all()
    rp = Entity.objects.filter(is_rp=True).all()
    return respond_to(request,{'text/html': 'apps/event/list.html'},{'rps':rp.all(),'idps':idp.all()})