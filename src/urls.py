from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

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
                       # url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                       #     {'document_root': settings.STATIC_ROOT, 'show_indexes': True}, name='static'),

                       url(r'^login/?', 'django.contrib.auth.views.login', name='login'),
                       url(r'^register/?', 'user.views.register', name='register'),
                       url(r'^logout/?', 'user.views.logout', name='logout'),

                       url(r'^categories/?', 'product.views.categories', name='categories'),
                       url(r'^category/(?P<id>\d+)/?', 'product.views.category', name='category'),
                       url(r'^category-products/?', 'product.views.category_products', name='category_products'),

                       url(r'^product/(?P<id>\d+)/?', 'product.views.product', name='product'),

                       url(r'^qr/?', 'product.views.qr', name='qr'),

                       url(r'^callback/(?P<plat>(s|t))/?', 'main.views.callback', name='callback'),

                       url(r'^comment/(?P<product_id>\d+)/?', 'comment.views.comment_list', name='comment_list'),
                       url(r'^comment/add/?', 'comment.views.comment_add', name='comment_add'),
                       url(r'^comment/del/?', 'comment.views.comment_del', name='comment_del'),
)

urlpatterns += staticfiles_urlpatterns()
