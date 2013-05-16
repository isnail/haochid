__author__ = 'biyanbing'

from django.db import models
from django.contrib.auth.models import AbstractBaseUser

import cn_key

gender_choices = (
    ('m', cn_key._male),
    ('f', cn_key._female),
    ('n', cn_key._unknown),
)


class User(AbstractBaseUser):
    uid = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(cn_key._email, null=True, blank=True)
    gender = models.CharField(cn_key._gender, max_length=1, choices=gender_choices, default=gender_choices[2][0])
    avatar = models.CharField(cn_key._avatar, max_length=511, null=True, blank=True)
    location = models.CharField(cn_key._location, max_length=511, null=True, blank=True)
    login_location = models.CharField('%s%s' % (cn_key._login, cn_key._location), max_length=255, null=True, blank=True)
    ip = models.IPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'uid'


    class Meta:
        verbose_name = cn_key._user
        verbose_name_plural = cn_key._user


class UserPlat(models.Model):
    user = models.ForeignKey(User, verbose_name=cn_key._user)
    plat = models.ForeignKey('plat.Plat', verbose_name=cn_key._plat)

    class Meta:
        verbose_name = '%s%s' % (cn_key._plat, cn_key._user)
        verbose_name_plural = '%s%s' % (cn_key._plat, cn_key._user)



