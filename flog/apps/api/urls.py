"""
Created on Apr 13, 2012

@author: leifj
"""
from __future__ import absolute_import

from django.conf.urls import url
from flog.apps.api import views

urlpatterns = [
    url(r'^import$', views.iprt),
    url(r'^eduroam/checkrealm/$', views.eduroamcheck),
    url(r'^websso/checkentity/$', views.webssocheck),
    url(r'^eduroam/latest/$', views.importcheck, kwargs={'event_type': 'eduroam'}),
    url(r'^websso/latest/$', views.importcheck, kwargs={'event_type': 'websso'}),
]
