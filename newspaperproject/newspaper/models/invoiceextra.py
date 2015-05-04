from django.db import models

import datetime
from datetime import date

from client import Client
from invoiceextraitem import InvoiceExtraItem

class InvoiceExtra(models.Model):
 
  client = models.ForeignKey(Client) 
  invoiceExtraItem = models.ManyToManyField(InvoiceExtraItem) 

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

