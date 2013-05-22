__author__ = 'biyanbing'

from django.db import models

import cn_key
from utils import *

class Comment(models.Model):
    user = models.ForeignKey('user.User', verbose_name=cn_key._user)
    product = models.ForeignKey('product.Product', verbose_name=cn_key._product)
    parent = models.ForeignKey('self', null=True, blank=True, verbose_name=cn_key._parent_comment)
    content = models.CharField(cn_key._content, max_length=254)
    status = models.BooleanField(cn_key._status, default=True)
    is_send = models.BooleanField(cn_key._is_send, default=True)
    created_time = models.DateTimeField(cn_key._created_time, auto_now_add=True)

    def __unicode__(self):
        return u'#%s #%s #%s' % (self.user, self.product, self.id)

    def to_dict(self, user=None):
        data = {}
        if user and self.user.id == user.id:
            data['author'] = True
        data['id'] = self.id
        data['content'] = replace_html_tags(self.content) if self.status else None
        data['created_time'] = str(self.created_time)
        data['user'] = {}
        data['user']['name'] = self.user.get_short_name()
        data['user']['avatar'] = self.user.avatar if self.user.avatar else ''
        data['user']['id'] = self.user.id
        return data

    class Meta:
        verbose_name = cn_key._comment
        verbose_name_plural = cn_key._comment
        ordering = ('-created_time', )
