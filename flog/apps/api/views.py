'''
Created on Apr 13, 2012

@author: leifj
'''
from flog.apps.event.models import import_event, import_events
import logging
from django.http import HttpResponse, HttpResponseBadRequest


def iprt(request):
    if request.method == "POST":
        import_events(request.body)
        return HttpResponse("imported stuff", status=201)
    else:
        return HttpResponseBadRequest("what?")