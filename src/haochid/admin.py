__author__ = 'biyanbing'
from django.contrib import admin
from django import forms

from haochid.models import *
from utils import save_to_oss


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
        return '<span style="color:red;">No Cover</span>'
    return '<a href="%s" target="_blank"><img src="%s" width=100px /></a>' % (obj.cover, obj.cover)


def category(obj):
    category.allow_tags = True
    if not obj.category:
        return ''
    return '&nbsp;,&nbsp;'.join([c.name for c in obj.category.all()])


def tag(obj):
    tag.allow_tags = True
    if not obj.tag:
        return ''
    return '&nbsp;,&nbsp;'.join([t.name for t in obj.tag.all()])


cover.short_description = cn_key._cover
category.short_description = cn_key._category
tag.short_description = cn_key._tag


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        widgets = {
            'cover': forms.FileInput()
        }


class CategoryInline(admin.TabularInline):
    model = Product.category.through
    verbose_name = cn_key._category
    verbose_name_plural = cn_key._category


class TagInline(admin.TabularInline):
    model = Product.tag.through
    verbose_name = cn_key._tag
    verbose_name_plural = cn_key._tag


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title', cover, 'content', category, tag, 'status', 'vote_up', 'vote_down', 'share', 'update_time',
        'created_time')
    list_filter = ('category', 'tag', )
    readonly_fields = ('vote_up', 'vote_down', 'share')
    ordering = ('-update_time', '-created_time', )
    form = ProductForm
    inlines = [CategoryInline, TagInline]
    exclude = ('category', 'tag', )
    search_fields = ('title', 'content', )


    def save_model(self, request, obj, form, change):
        cover = form.cleaned_data.get('cover')
        if cover:
            cover = request.FILES.get('cover')
            path = 'images/products/%s/%s' % (obj.pk, cover.name)
            obj.cover = save_to_oss(path, cover.read(), cover.content_type)
            obj.save()


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Product, ProductAdmin)

