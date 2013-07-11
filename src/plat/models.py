__author__ = 'biyanbing'
from django.db import models

import cn_key

plat_choices = (
    ('t', cn_key._tencent),
    ('s', cn_key._sina),
    ('l', cn_key._local),
    ('q', 'QQ'),
    ('o', cn_key._other),
)

class Plat(models.Model):
    name = models.CharField(cn_key._name, max_length=1, choices=plat_choices, default=plat_choices[2][0], unique=True)
    app_key = models.CharField(cn_key._app_key, max_length=255, null=True, blank=True)
    app_secret = models.CharField(cn_key._app_secret, max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = cn_key._plat
        verbose_name_plural = cn_key._plat
        # app_label = cn_key._plat
        # db_table = 'plat'