"""
Created on Apr 13, 2012

@author: leifj
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.event.views',
    # websso
    url(r'^websso/origin/(?P<pk>\d+)/$', view='by_origin'),
    url(r'^websso/rp/(?P<pk>\d+)/$', view='by_rp'),
    url(r'^websso/authentication-flow/$', view='auth_flow'),
    url(r'^websso/$', view='websso_entities'),
    # eduroam
    url(r'^eduroam/to/(?P<pk>\d+)/$', view='to_realm'),
    url(r'^eduroam/from/(?P<pk>\d+)/$', view='from_realm'),
    url(r'^eduroam/authentication-flow/$', view='auth_flow', kwargs={'protocol': 'eduroam'}),
    url(r'^eduroam/(?P<country_name>[ \w]+)/$', view='eduroam_realms'),
    url(r'^eduroam/$', view='eduroam_realms'),
    # index
    url(r'^$', view='index'),
)