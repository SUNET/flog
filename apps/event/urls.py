"""
Created on Apr 13, 2012

@author: leifj
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.event.views',
    url(r'^origin/(?P<pk>\d+)/$', view='by_origin'),
    #url(r'^origin/(?P<pk>\d+)/min=(?P<default_min>\d+)&max=(?P<default_max>\d+)$', view='by_origin'),
    url(r'^rp/(?P<pk>\d+)/$', view='by_rp'),
    #url(r'^rp/(?P<pk>\d+)/min=(?P<default_min>\d+)&max=(?P<default_max>\d+)$', view='by_rp'),
    url(r'^authentication-flow/$', view='auth_flow'),
    url(r'^authentication-flow/threshold=(?P<value_threshold>\d+)$', view='auth_flow'),
    url(r'^authentication-flow/min=(?P<default_min>\d+)&max=(?P<default_max>\d+)$', view='auth_flow'),
    url(r'^authentication-flow/min=(?P<default_min>\d+)&max=(?P<default_max>\d+)&threshold=(?P<value_threshold>\d+)$', view='auth_flow'),
    url(r'^entities/$', view='entities'),
)