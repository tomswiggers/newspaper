from django.db import models

import datetime
from datetime import date

from client import Client

class InvoiceExtra(models.Model):
 
  client = models.ForeignKey(Client) 
  description = models.CharField('Beschrijving', max_length=255)
  number = models.IntegerField('Aantal')
  amount = models.FloatField()

  class Meta:
    app_label = 'newspaper'
    verbose_name = 'Extra facturatie'
    verbose_name_plural = 'Extra facturatie'

  def __repr__(self):
    return self.getString()

  def __str__(self):
    return self.getString()

  def getString(self):
    return str(self.client) + ': ' + self.description

