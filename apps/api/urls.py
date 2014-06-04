'''
Created on Apr 13, 2012

@author: leifj
'''

from django.conf.urls import patterns, url

urlpatterns = patterns('apps.api.views',
    url(r'^import$',view='iprt'),
    url(r'^eduroam/checkrealm/$',view='eduroamcheck'),
    url(r'^websso/checkentity/$', view='webssocheck'),
)