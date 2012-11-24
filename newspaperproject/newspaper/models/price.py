from django.db import models
from newspaper.models import Item

import datetime
from datetime import date

class Price(models.Model):
  begindate = models.DateField()
  enddate = models.DateField()
  price = models.FloatField('Prijs')
  item = models.ForeignKey(Item)

  class Meta:
    app_label = 'newspaper'
    ordering = ['item']
    verbose_name = 'Prijs'
    verbose_name_plural = 'Prijzen'

  def __str__(self):
    return str(self.item.name) + ': ' + str(self.price) + ' (' + str(self.begindate) + ' - ' + str(self.enddate) + ')'

