"""
Created on Apr 13, 2012

@author: leifj
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.event.views',
    url(r'^websso/origin/(?P<pk>\d+)/$', view='by_origin'),
    #url(r'^origin/(?P<pk>\d+)/min=(?P<default_min>\d+)&max=(?P<default_max>\d+)$', view='by_origin'),
    url(r'^websso/rp/(?P<pk>\d+)/$', view='by_rp'),
    #url(r'^rp/(?P<pk>\d+)/min=(?P<default_min>\d+)&max=(?P<default_max>\d+)$', view='by_rp'),
    url(r'^websso/authentication-flow/$', view='auth_flow'),
    url(r'^websso/authentication-flow/threshold=(?P<value_threshold>\d+)$', view='auth_flow'),
    url(r'^websso/authentication-flow/min=(?P<default_min>\d+)&max=(?P<default_max>\d+)$', view='auth_flow'),
    url(r'^websso/authentication-flow/min=(?P<default_min>\d+)&max=(?P<default_max>\d+)&threshold=(?P<value_threshold>\d+)$', view='auth_flow'),
    url(r'^websso/$', view='websso_entities'),
    url(r'^eduroam/$', view='eduroam_entities'),
    url(r'^$', view='index'),
)