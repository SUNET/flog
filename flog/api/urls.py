'''
Created on Apr 13, 2012

@author: leifj
'''

from django.conf.urls import patterns, url

urlpatterns = patterns('api.views',
    url(r'^import$',view='iprt'),
)