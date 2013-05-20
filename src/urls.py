from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'haochid.views.home', name='home'),
    # url(r'^/', include(user.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', 'product.views.index', name='index'),
    url(r'^static/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),

    url(r'^login/?', 'django.contrib.auth.views.login', name='login'),
    url(r'^register/?', 'user.views.register', name='register'),

    url(r'^categories/?', 'product.views.categories', name='categories'),
    url(r'^category/(?P<id>\d+)/?', 'product.views.category', name='category'),
    url(r'^category-products/?', 'product.views.category_products', name='category_products'),

    url(r'^product/(?P<id>\d+)/?', 'product.views.product', name='product'),


    url(r'^qr/?', 'product.views.qr', name='qr'),
)
