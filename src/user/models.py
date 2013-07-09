__author__ = 'biyanbing'

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from django.core.mail import send_mail

import cn_key

gender_choices = (
    ('m', cn_key._male),
    ('f', cn_key._female),
    ('n', cn_key._no_say),
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
    access_token = models.CharField(max_length=255, null=True, blank=True)
    expires_in = models.IntegerField(null=True, blank=True)
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

    @property
    def name(self):
        return self.get_short_name()

    def get_short_name(self):
        return self.nick_name if self.nick_name else self.uid.split('@')[0]

    def get_full_name(self):
        return self.uid

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    class Meta:
        verbose_name = cn_key._user
        verbose_name_plural = cn_key._user
        swappable = 'AUTH_USER_MODEL'


class UserFriendShip(models.Model):
    user = models.ForeignKey(User, verbose_name=cn_key._user)
    friends = models.ManyToManyField(User, verbose_name=cn_key._user_friend)

    class Meta:
        verbose_name = cn_key._user_friend_ship
        verbose_name_plural = cn_key._user_friend_ship


class LBSGroup(models.Model):
    owner = models.ForeignKey(User, verbose_name=cn_key._owner)
    members = models.ManyToManyField(User, verbose_name=cn_key._members)
    name = models.CharField(cn_key._name, max_length=16)
    max_member_count = models.PositiveIntegerField(cn_key._max_member_count, default=200)
    level = models.PositiveSmallIntegerField(cn_key._level, default=1)
    location = models.CharField(cn_key._location, max_length=255)
    x_coordinate = models.CharField(cn_key, max_length=32)
    y_coordinate = models.CharField(cn_key, max_length=32)
    description = models.CharField(cn_key._description, max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = cn_key._lbs_group
        verbose_name_plural = cn_key._lbs_group


MESSAGE_CHOICES = (
    ('F', 'Friend', ),
    ('G', 'Group', ),
    ('S', 'System', ),
)

class Message(models.Model):
    user = models.ForeignKey(User, verbose_name=cn_key._user)
    content = models.CharField(cn_key._content, max_length=255)
    type = models.CharField(cn_key._type, max_length=1, choices=MESSAGE_CHOICES)
    to_group = models.ForeignKey(LBSGroup, verbose_name=cn_key._lbs_group, null=True, blank=True)
    to_user = models.ForeignKey(User, verbose_name=cn_key._user_friend, null=True, blank=True)
    is_read = models.BooleanField(cn_key._is_read, default=False)
    is_deleted = models.BooleanField(cn_key._is_deleted, default=False)
    created_time = models.DateTimeField(cn_key._created_time, auto_now_add=True)

    class Meta:
        verbose_name = cn_key._message
        verbose_name_plural = cn_key._message
