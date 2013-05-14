__author__ = 'biyanbing'
from django.contrib import admin

from haochid.models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_time', )
    fields = ('name', )
    readonly_fields = ("created_time", )


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_time', )
    fields = ('name', )
    readonly_fields = ("created_time", )


def cover(obj):
    cover.allow_tags = True
    if not obj.cover:
        return '<span style="color:red;">NO LOGO</span>'
    return '<img src="%s" width=100px />' % obj.cover.url


def category(obj):
    category.allow_tags = True
    if not obj.category:
        return ''
    return '&nbsp;,&nbsp;'.join([c.name for c in obj.category])


def tag(obj):
    tag.allow_tags = True
    if not obj.tag:
        return ''
    return '&nbsp;,&nbsp;'.join([t.name for t in obj.tag])


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', category, tag, 'vote_up', 'vote_down', 'share', cover, )
    readonly_fields = ('vote_up', 'vote_down', 'share')
    ordering = ('-update_time', '-created_time', )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Product, ProductAdmin)

