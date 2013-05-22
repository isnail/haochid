__author__ = 'Dany Bee'

from django.db.models import signals
from django.db import connections
from django.db import router
from django.core.management.color import no_style

from models import Plat
import models as site_app

def create_default_plat(app, created_models, verbosity, db, **kwargs):
    Plat.objects.all().delete()
    sequence_sql = connections[db].ops.sequence_reset_sql(no_style(), [Plat])
    if sequence_sql:
        cursor = connections[db].cursor()
        for command in sequence_sql:
            cursor.execute(command)
    Plat(pk=1, name='s', app_key='3839507357', app_secret='984b935c0180dd2af1017550c131350f').save(using=db)
    sequence_sql = connections[db].ops.sequence_reset_sql(no_style(), [Plat])
    if sequence_sql:
        cursor = connections[db].cursor()
        for command in sequence_sql:
            cursor.execute(command)
    Plat(pk=2, name='t', app_key='801167659', app_secret='db437510eb1ccf454f820a06d32d4cf9').save(using=db)
    sequence_sql = connections[db].ops.sequence_reset_sql(no_style(), [Plat])
    if sequence_sql:
        cursor = connections[db].cursor()
        for command in sequence_sql:
            cursor.execute(command)
    Plat(pk=3, name='l', app_key='', app_secret='').save(using=db)
    sequence_sql = connections[db].ops.sequence_reset_sql(no_style(), [Plat])
    if sequence_sql:
        cursor = connections[db].cursor()
        for command in sequence_sql:
            cursor.execute(command)
    Plat(pk=4, name='o', app_key='', app_secret='').save(using=db)
    sequence_sql = connections[db].ops.sequence_reset_sql(no_style(), [Plat])
    if sequence_sql:
        cursor = connections[db].cursor()
        for command in sequence_sql:
            cursor.execute(command)

signals.post_syncdb.connect(create_default_plat, sender=site_app)
