__author__ = 'biyanbing'

from django.contrib import admin

from models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('uid', 'email', 'gender', 'location', 'login_location', )

admin.site.register(User, UserAdmin)