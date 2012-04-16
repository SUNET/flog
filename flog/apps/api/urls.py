'''
Created on Apr 13, 2012

@author: leifj
'''

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('flog.apps.api.views',
    url(r'^import$',view='iprt'),
)