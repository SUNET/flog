"""
Created on Apr 13, 2012

@author: leifj
"""
from __future__ import absolute_import

from django.conf.urls import url
from flog.apps.event import views

urlpatterns = [
    # websso
    url(r'^websso/origin/(?P<pk>\d+)/$', views.by_origin),
    url(r'^websso/rp/(?P<pk>\d+)/$', views.by_rp),
    url(r'^websso/authentication-flow/$', views.auth_flow),
    url(r'^websso/$', views.websso_entities),
    # eduroam
    url(r'^eduroam/to/(?P<pk>\d+)/$', views.to_realm),
    url(r'^eduroam/from/(?P<pk>\d+)/$', views.from_realm),
    url(r'^eduroam/authentication-flow/$', views.auth_flow, kwargs={'protocol': 'eduroam'}),
    url(r'^eduroam/(?P<country_code>[\w]+)/$', views.eduroam_realms),
    url(r'^eduroam/$', views.eduroam_realms),
    # index
    url(r'^$', views.index),
]