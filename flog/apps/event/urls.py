"""
Created on Apr 13, 2012

@author: leifj
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('flog.apps.event.views',
    url(r'^origin/(?P<pk>\d+)/$', view='by_origin'),
    url(r'^rp/(?P<pk>\d+)/$', view='by_rp'),
    url(r'^entities/?$', view='entities'),
)