from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'haochid.views.home', name='home'),
    # url(r'^haochid/', include('haochid.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', 'haochid.views.index', name='index'),
    (r'^static/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),
)
