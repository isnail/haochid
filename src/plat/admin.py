__author__ = 'biyanbing'

from django.contrib import admin

from models import *

class PlatAdmin(admin.ModelAdmin):
    list_display = ('name', 'app_key', 'app_secret', )

admin.site.register(Plat, PlatAdmin)