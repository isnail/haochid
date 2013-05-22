__author__ = 'biyanbing'

from django.contrib import admin

from models import *


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'nick_name', 'email', 'plat', 'gender', 'location', 'login_location', 'ip', 'is_staff', 'is_active',
        'is_superuser', 'expires_in',
        'date_joined', )
    list_filter = ('plat', 'gender', )
    search_fields = ('uid', 'nick_name', 'email', )
    fieldsets = (
        (None, {
            'fields': ('uid', 'email', 'expires_in',)
        }),
        (cn_key._info, {
            'classes': ('collapse', ),
            'fields': ('gender', 'location', 'login_location', 'ip', )
        }),
        (cn_key._manage, {
            'classes': ('collapse', ),
            'fields': ('is_superuser', 'groups', 'user_permissions', 'is_staff', 'is_active', )
        })
    )


admin.site.register(User, UserAdmin)
