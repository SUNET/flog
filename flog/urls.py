from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from flog.apps.event import views as event_views

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', event_views.index),
    url(r'^event/', include('flog.apps.event.urls')),
    url(r'^api/', include('flog.apps.api.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
