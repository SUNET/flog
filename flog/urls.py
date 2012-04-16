from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from flog.multiresponse import respond_to
from django.conf import settings
from django.http import HttpResponseRedirect

admin.autodiscover()

def welcome(request):
    return respond_to(request, {'text/html':HttpResponseRedirect('/event/entities')})

urlpatterns = patterns('',
    (r'^admin-media/(?P<path>.*)$',                 'django.views.static.serve',{'document_root': settings.ADMIN_MEDIA_ROOT}),
    (r'^site-media/(?P<path>.*)$',                  'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    (r'^admin/',                                    include(admin.site.urls)),
    (r'^$',                                         welcome),
    (r'^event/',                                   include("flog.apps.event.urls")),
    (r'^api/',                                     include("flog.apps.api.urls"))
)