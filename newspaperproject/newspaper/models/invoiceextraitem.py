from django.db import models

import datetime
from datetime import date

class InvoiceExtraItem(models.Model):
  BTW_VALUES = (
    (0, u'0.0%'),
    (6, u'6.0%'),
    (21, u'21.0%'),
  )

  description = models.CharField('Beschrijving', max_length=255)
  number = models.IntegerField('Aantal')
  amount = models.FloatField()
  btw = models.IntegerField(choices=BTW_VALUES)

  class Meta:
    app_label = 'newspaper'
    verbose_name = 'Extra facturatie item'
    verbose_name_plural = 'Extra facturatie items'

  def __repr__(self):
    return self.getString()

  def __str__(self):
    return self.getString()

  def getString(self):
    return self.description

