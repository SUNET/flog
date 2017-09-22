"""
Created on Apr 13, 2012

@author: leifj, lundberg
"""
from __future__ import absolute_import

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
from flog.apps.event.models import import_events
from flog.apps.event.models import Entity, EduroamRealm, Event, EduroamEvent
import json
from datetime import datetime, timedelta


def normalize_whitespace(s):
    return ' '.join(s.split())


@csrf_exempt
def iprt(request):
    if request.method == "POST":
        import_events(request.body)
        return HttpResponse("imported stuff", status=201)
    else:
        return HttpResponseBadRequest("what?")


def eduroamcheck(request):
    now = datetime.utcnow()
    realm = request.GET.get('realm', None)
    try:
        realm = EduroamRealm.objects.get(realm=realm)
    except ObjectDoesNotExist:
        msg = '''
            You can find documentation for setting up F-ticks for eduroam at
            https://confluence.terena.org/display/H2eduroam/How+to+deploy+eduroam+at+national+level
            '''
        result = {
            'status': 404,
            'error': 'Could not find realm %s' % realm,
            'message': normalize_whitespace(msg)
        }
        return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), status=404, mimetype='application/json')
    result = {
        'latest_realm_event': None,
        'latest_institution_event': None
    }
    try:
        result['latest_realm_event'] = realm.realm_events.filter(ts__gt=now-timedelta(days=1)).latest('ts').ts
    except ObjectDoesNotExist:
        pass
    try:
        result['latest_institution_event'] = realm.institution_events.filter(ts__gt=now-timedelta(days=1)).latest('ts').ts
    except ObjectDoesNotExist:
        pass
    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), status=201, mimetype='application/json')


def webssocheck(request):
    now = datetime.utcnow()
    uri = request.GET.get('uri', None)
    try:
        entity = Entity.objects.get(uri=uri)
    except ObjectDoesNotExist:
        msg = '''
            You can find documentation for setting up F-ticks for WebSSO at
            https://portal.nordu.net/display/SWAMID/SAML+f-ticks+for+Shibboleth
            '''
        result = {
            'status': 404,
            'error': 'Could not find entity %s' % uri,
            'message': normalize_whitespace(msg)
        }
        return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), status=404, mimetype='application/json')
    result = {
        'latest_origin_event': None,
        'latest_rp_event': None
    }
    try:
        result['latest_origin_event'] = entity.origin_events.filter(ts__gt=now-timedelta(days=1)).latest('ts').ts
    except ObjectDoesNotExist:
        pass
    try:
        result['latest_rp_event'] = entity.rp_events.filter(ts__gt=now-timedelta(days=1)).latest('ts').ts
    except ObjectDoesNotExist:
        pass
    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), status=201, mimetype='application/json')


def importcheck(request, event_type):
    if event_type == "websso":
        latest_event = Event.objects.latest('ts')
    elif event_type == "eduroam":
        latest_event = EduroamEvent.objects.latest('ts')
    else:
        msg = '''
            This is a monitor end point.
            '''
        result = {
            'status': 404,
            'error': 'Could not find event type %s' % event_type,
            'message': normalize_whitespace(msg)
        }
        return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), status=404, mimetype='application/json')
    result = {
        'event_type': event_type,
        'latest_event': latest_event.ts
    }
    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), status=201, mimetype='application/json')

