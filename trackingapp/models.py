from __future__ import unicode_literals

from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=25)
    url = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Expansion(models.Model):
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return self.name


class SourceExpansion(models.Model):
    expansion = models.ForeignKey(Expansion)
    source = models.ForeignKey(Source)


class Card(models.Model):
    name = models.CharField(max_length=50)
    expansion = models.ForeignKey(Expansion)

    def __unicode__(self):
        return self.name


class Stock(models.Model):
    card = models.ForeignKey(Card)
    source = models.ForeignKey(Source)
    date = models.DateField()

    high = models.FloatField()
    medium = models.FloatField()
    low = models.FloatField()

    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return "{} {}".format(self.card.name, self.date)
