__author__ = 'biyanbing'

from django.contrib import admin

from models import *

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'parent', 'content', 'status', 'is_send', 'created_time')
    list_filter = ('status', 'is_send')
    search_fields = ('content', )

admin.site.register(Comment, CommentAdmin)
