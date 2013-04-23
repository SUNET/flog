'''
Created on Apr 13, 2012

@author: leifj
'''

from apps.event.models import import_event, import_events
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def iprt(request):
    if request.method == "POST":
        import_events(request.body)
        return HttpResponse("imported stuff", status=201)
    else:
        return HttpResponseBadRequest("what?")