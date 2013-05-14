__author__ = 'biyanbing'
import datetime

from django.db import models

import cn_key


class Category(models.Model):
    name = models.CharField(cn_key._name, max_length=32, unique=True)
    created_time = models.DateTimeField(cn_key._created_time, auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = cn_key._category
        verbose_name_plural = cn_key._category


class Tag(models.Model):
    name = models.CharField(cn_key._name, max_length=32, unique=True)
    created_time = models.DateTimeField(cn_key._created_time, auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = cn_key._tag
        verbose_name_plural = cn_key._tag


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
    cover = models.CharField(cn_key._cover, max_length=800, null=True, blank=True)
    content = models.TextField(cn_key._content)
    vote_up = models.SmallIntegerField(cn_key._vote_up, default=0)
    vote_down = models.SmallIntegerField(cn_key._vote_down, default=0)
    share = models.SmallIntegerField(cn_key._share, default=0)
    status = models.CharField(cn_key._status, max_length=1, choices=product_status_choices,
                              default=product_status_choices[0][0])
    created_time = models.DateTimeField(cn_key._created_time, auto_now_add=True)
    update_time = models.DateTimeField(cn_key._update_time, auto_now=True, null=True, blank=True)

    def to_dict(self):
        return {
            'title': self.title,
            'category': [{'id': c.id, 'name': c.name} for c in self.category],
            'tag': [{'id': t.id, 'name': t.name} for t in self.tag],
            'cover': self.cover.url if self.cover else '',
            'vote_up': self.vote_up,
            'vote_down': self.vote_down
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


class DailyRecommended(models.Model):
    product = models.ForeignKey(Product)
    date = models.DateField()
    reason = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.product

    class Meta:
        ordering = ('-date', 'product__vote_up', )
        unique_together = ('product', 'date', )


class ProductStatistic(models.Model):
    product = models.CharField(max_length=11)
    point = models.IntegerField()


class ShareTrack(models.Model):
    user = models.ForeignKey('user.User')
    product = models.ForeignKey(Product)
    plat = models.CharField(max_length=32)
    created_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '#User-%s share #Product-%s to %s' % (self.user, self.product, self.plat)


vote_status_choices = (
    ('u', 'UP'),
    ('d', 'DOWN'),
    ('c', 'CANCEL')
)


class VoteTrack(models.Model):
    user = models.ForeignKey('user.User')
    product = models.ForeignKey(Product)
    vote_status = models.CharField(max_length=1, choices=vote_status_choices)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product', )


