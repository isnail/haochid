__author__ = 'biyanbing'

from django.db import models

class Plat(models.Model):
    name = models.CharField(max_length=32)
    status = models.BooleanField(default=False)

gender_choices = (
    ('m', 'Boy'),
    ('w', 'Girl'),
    ('n', 'Unknown')
)

class User(models.Model):
    email = models.EmailField(null=True, blank=True)
    pwd = models.CharField(max_length=32, null=True, blank=True)
    uid = models.CharField(max_length=255, null=True, blank=True)
    plat = models.ManyToManyField(Plat, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=gender_choices, default=gender_choices[2][0])
    avatar = models.CharField(max_length=255, null=True, blank=True)


