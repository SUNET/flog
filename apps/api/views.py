'''
Created on Apr 13, 2012

@author: leifj
'''

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
from apps.event.models import import_events
from apps.event.models import Entity, EduroamRealm
import json

@csrf_exempt
def iprt(request):
    if request.method == "POST":
        import_events(request.body)
        return HttpResponse("imported stuff", status=201)
    else:
        return HttpResponseBadRequest("what?")


def eduroamcheck(request):
    realm = request.GET.get('realm', None)
    realm = get_object_or_404(EduroamRealm, realm=realm)
    result = {
        'latest_realm_event': None,
        'latest_institution_event': None
    }
    try:
        result['latest_realm_event'] = realm.realm_events.latest('ts').ts
    except ObjectDoesNotExist:
        pass
    try:
        result['latest_institution_event'] = realm.institution_events.latest('ts').ts
    except ObjectDoesNotExist:
        pass
    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), status=201, mimetype='application/json')


def webssocheck(request):
    uri = request.GET.get('uri', None)
    entity = get_object_or_404(Entity, uri=uri)
    result = {
        'latest_origin_event': None,
        'latest_rp_event': None
    }
    try:
        result['latest_origin_event'] = entity.origin_events.latest('ts').ts
    except ObjectDoesNotExist:
        pass
    try:
        result['latest_rp_event'] = entity.rp_events.latest('ts').ts
    except ObjectDoesNotExist:
        pass
    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), status=201, mimetype='application/json')

