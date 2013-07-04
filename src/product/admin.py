__author__ = 'biyanbing'
import logging, uuid

from django.contrib import admin
from django import forms
from django.contrib.admin import SimpleListFilter

from models import *
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
    return '<a href="%s" target="_blank"><img src="%s" width=100px /></a>' % (obj.cover.url, obj.cover.url)


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


def is_recommend(obj):
    is_recommend.allow_tags = True
    is_recommend.boolean = True
    if DailyRecommended.objects.filter(product=obj):
        return True
    return False
#
# class AuthorFilter(SimpleListFilter):
#     title = cn_key._author
#     parameter_name = 'author'
#
#     def lookups(self, request, model_admin):
#         return [[q.pk, q.uid] for q in User.objects.filter(is_staff=True)]
#
#     def queryset(self, request, queryset):
#         return queryset.filter(author=self.value())


cover.short_description = cn_key._cover
category.short_description = cn_key._category
tag.short_description = cn_key._tag
is_recommend.short_description = cn_key._recommend


class CategoryInline(admin.TabularInline):
    model = Product.category.through
    verbose_name = cn_key._category
    verbose_name_plural = cn_key._category


class TagInline(admin.TabularInline):
    model = Product.tag.through
    verbose_name = cn_key._tag
    verbose_name_plural = cn_key._tag


def add_recommend(modeladmin, req, qs):
    date = datetime.date.today()
    for q in qs:
        try:
            DailyRecommended.objects.get(product=q, date=date)
        except DailyRecommended.DoesNotExist:
            DailyRecommended.objects.create(product=q, date=date)


def del_recommend(modleadmin, req, qs):
    for q in qs:
        if isinstance(q, Product):
            DailyRecommended.objects.filter(product=q).delete()
        else:
            q.delete()


add_recommend.short_description = '%s %s' % (cn_key._add, cn_key._recommend)
del_recommend.short_description = '%s %s' % (cn_key._del, cn_key._recommend)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title', cover, 'author', 'content', category, tag, 'status', is_recommend, 'vote_up', 'vote_down', 'share',
        'update_time',
        'created_time')
    list_filter = ('category', 'tag', )
    readonly_fields = ('vote_up', 'vote_down', 'share')
    ordering = ('-update_time', '-created_time', )
    inlines = [CategoryInline, TagInline]
    exclude = ('category', 'tag', )
    search_fields = ('title', 'content', )
    actions = (add_recommend, del_recommend, )


    def save_model(self, request, obj, form, change):
        if obj.cover:
            obj.cover = None
        obj.save()
        cover = request.FILES.get('cover')
        if cover:
            path = 'images/products/%s/%s' % (obj.pk, cover.name)
            obj.cover = save_to_oss(path, cover.read(), cover.content_type)
        if not change:
            obj.author = request.user
        obj.save()


class DailyRecommendedForm(forms.ModelForm):
    class Meta:
        model = DailyRecommended
        widgets = {
            'reason': forms.Textarea()
        }


class DailyRecommendedAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'reason', )
    list_filter = ('date', )
    ordering = ('-date', )
    search_fields = ('product__title', )
    form = DailyRecommendedForm
    readonly_fields = ('product', )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(DailyRecommended, DailyRecommendedAdmin)

