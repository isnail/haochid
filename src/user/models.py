__author__ = 'biyanbing'

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

import cn_key

gender_choices = (
    ('m', cn_key._male),
    ('f', cn_key._female),
    ('n', cn_key._unknown),
)


class UserPlat(models.Model):
    plat = models.ForeignKey('plat.Plat', verbose_name=cn_key._plat, null=True, blank=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def create_user(self, uid, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not uid:
            raise ValueError('The given username must be set')
        user = self.model(uid=uid,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, uid, password, **extra_fields):
        u = self.create_user(uid, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class User(AbstractBaseUser, PermissionsMixin, UserPlat):
    uid = models.CharField(cn_key._account, max_length=255, unique=True, db_index=True)
    email = models.EmailField(cn_key._email, null=True, blank=True)
    nick_name = models.CharField(cn_key._nick_name, max_length=32, null=True, blank=True)
    gender = models.CharField(cn_key._gender, max_length=1, choices=gender_choices, default=gender_choices[2][0])
    avatar = models.CharField(cn_key._avatar, max_length=511, null=True, blank=True)
    location = models.CharField(cn_key._location, max_length=511, null=True, blank=True)
    login_location = models.CharField('%s%s' % (cn_key._login, cn_key._location), max_length=255, null=True, blank=True)
    ip = models.IPAddressField(null=True, blank=True)
    is_staff = models.BooleanField(cn_key._is_staff, default=False)
    is_active = models.BooleanField(cn_key._is_active, default=True)
    date_joined = models.DateTimeField(cn_key._created_time, default=timezone.now)

    USERNAME_FIELD = 'uid'
    objects = CustomUserManager()

    def get_short_name(self):
        return self.nick_name if self.nick_name else ''

    class Meta:
        verbose_name = cn_key._user
        verbose_name_plural = cn_key._user
        swappable = 'AUTH_USER_MODEL'




