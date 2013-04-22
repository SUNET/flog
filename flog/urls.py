from django.conf.urls import patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'apps.event.views.entities'),
    (r'^event/', include("apps.event.urls")),
    (r'^api/', include("apps.api.urls"))
)