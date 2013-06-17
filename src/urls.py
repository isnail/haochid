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
                       url(r'^ajax-login/?', 'user.views.ajax_login', name='ajax_login'),
                       url(r'^register/?', 'user.views.register', name='register'),
                       url(r'^logout/?', 'user.views.logout', name='logout'),
                       url(r'^account/?', 'user.views.account', name='account'),
                       url(r'^password/?', 'user.views.change_password', name='change_password'),

                       url(r'^categories/?', 'product.views.categories', name='categories'),
                       url(r'^category/(?P<id>\d+)/?', 'product.views.category', name='category'),
                       url(r'^category-products/?', 'product.views.category_products', name='category_products'),

                       url(r'^product/(?P<id>\d+)/?', 'product.views.product', name='product'),
                       url(r'^product-info/(?P<id>\d+)/?', 'product.views.product_info', name='product_info'),
                       url(r'^hot/?$', 'product.views.hot_index', name='hot_index'),
                       url(r'^hot-list/((?P<page>\d+)/?)?', 'product.views.hot', name='hot'),
                       url(r'^new/?$', 'product.views.new_index', name='new_index'),
                       url(r'^new-list/((?P<page>\d+)/?)?', 'product.views.new', name='new'),
                       url(r'^recommend/?$', 'product.views.recommend_index', name='recommend_index'),
                       url(r'^recommend-list/((?P<page>\d+)/?)?', 'product.views.recommend', name='recommend'),

                       url(r'^vote/(?P<product_id>\d+)/((?P<vote>\w)/?)?', 'product.views.vote', name='vote'),


                       url(r'^qr/?', 'product.views.qr', name='qr'),

                       url(r'^callback/(?P<plat>(s|t))/?', 'main.views.callback', name='callback'),

                       url(r'^comment/(?P<product_id>\d+)/?', 'comment.views.comment_list', name='comment_list'),
                       url(r'^comment/add/?', 'comment.views.comment_add', name='comment_add'),
                       url(r'^comment/del/?', 'comment.views.comment_del', name='comment_del'),
)

urlpatterns += staticfiles_urlpatterns()

