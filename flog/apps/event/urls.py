"""
Created on Apr 13, 2012

@author: leifj
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('flog.apps.event.views',
    url(r'^origin/(.+)$',view='by_origin'),
    url(r'^rp/(.+)$',view='by_rp'),
    url(r'^entities/?$',view='entities'),
)