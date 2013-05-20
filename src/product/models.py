__author__ = 'biyanbing'
import datetime

from django.db import models
from django.core.urlresolvers import reverse

from user.models import User

import cn_key


class Category(models.Model):
    name = models.CharField(cn_key._name, max_length=32, unique=True)
    created_time = models.DateTimeField(cn_key._created_time, auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = cn_key._category
        verbose_name_plural = cn_key._category
        # app_label = cn_key._haochid
        # db_table = 'category'


class Tag(models.Model):
    name = models.CharField(cn_key._name, max_length=32, unique=True)
    created_time = models.DateTimeField(cn_key._created_time, auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = cn_key._tag
        verbose_name_plural = cn_key._tag
        # app_label = cn_key._haochid
        # db_table = 'tag'


product_status_choices = (
    ('A', cn_key._ok),
    ('I', cn_key._close),
    ('W', cn_key._waiting)
)


class Product(models.Model):
    now = datetime.datetime.today()
    title = models.CharField(cn_key._title, max_length=255)
    category = models.ManyToManyField(Category, null=True, blank=True, verbose_name=cn_key._category)
    tag = models.ManyToManyField(Tag, null=True, blank=True, verbose_name=cn_key._tag)
    cover = models.FileField(cn_key._cover, null=True, blank=True, upload_to='u')
    content = models.TextField(cn_key._content)
    vote_up = models.SmallIntegerField(cn_key._vote_up, default=0)
    vote_down = models.SmallIntegerField(cn_key._vote_down, default=0)
    share = models.SmallIntegerField(cn_key._share, default=0)
    status = models.CharField(cn_key._status, max_length=1, choices=product_status_choices,
                              default=product_status_choices[0][0])
    author = models.ForeignKey(User, verbose_name=cn_key._author, null=True, blank=True)
    created_time = models.DateTimeField(cn_key._created_time, auto_now_add=True)
    update_time = models.DateTimeField(cn_key._update_time, auto_now=True, null=True, blank=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': [{'id': c.id, 'name': c.name} for c in self.category.all()],
            'tag': [{'id': t.id, 'name': t.name} for t in self.tag.all()],
            'cover': self.cover.url if self.cover else '',
            'vote_up': self.vote_up,
            'vote_down': self.vote_down,
            'content': '%s...' % self.content[0:40],
            'url': reverse('product', kwargs={'id': self.id})
        }

    def increase_vote_up(self, point):
        self.vote_up = models.F('vote_up') + point
        self.save()

    def increase_vote_down(self, point):
        self.vote_down = models.F('vote_down') + point
        self.save()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = cn_key._product
        verbose_name_plural = cn_key._product
        ordering = ('-created_time', )
        # app_label = cn_key._haochid
        # db_table = 'product'


class DailyRecommended(models.Model):
    product = models.ForeignKey(Product, verbose_name=cn_key._product)
    date = models.DateField(cn_key._date)
    reason = models.CharField(cn_key._reason, max_length=255, null=True)

    def __unicode__(self):
        return self.product.title

    class Meta:
        ordering = ('-date', 'product__vote_up', )
        unique_together = ('product', 'date', )
        verbose_name = '%s%s' % (cn_key._daily, cn_key._recommend)
        verbose_name_plural = '%s%s' % (cn_key._daily, cn_key._recommend)
        # app_label = cn_key._haochid
        # db_table = 'daily_recommended'


class ProductStatistic(models.Model):
    product = models.CharField(max_length=11)
    point = models.IntegerField()

    # class Meta:
    #     app_label = cn_key._statistic
    #     db_table = 'product_statistic'


class ShareTrack(models.Model):
    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    plat = models.CharField(max_length=32)
    created_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '#User-%s share #Product-%s to %s' % (self.user, self.product, self.plat)

    # class Meta:
    #     app_label = cn_key._statistic
    #     db_table = 'shart_track'


vote_status_choices = (
    ('u', 'UP'),
    ('d', 'DOWN'),
    ('c', 'CANCEL')
)


class VoteTrack(models.Model):
    user = models.ForeignKey(User)
    product = models.ForeignKey(Product)
    vote_status = models.CharField(max_length=1, choices=vote_status_choices)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product', )
        # app_label = cn_key._statistic
        # db_table = 'vote_track'


