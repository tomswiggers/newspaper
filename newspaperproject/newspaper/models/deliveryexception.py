from django.db import models
from newspaper.models import Client
from newspaper.models import Item

import datetime
from datetime import date

class DeliveryException(models.Model):
  item = models.ForeignKey(Item)
  entrydate = models.DateField()
  
  class Meta:
    app_label = 'newspaper'
    ordering = ['entrydate']
    verbose_name = 'Levering uitzondering'
    verbose_name_plural = 'Levering uitzonderingen'

  def __str__(self):
    return self.item.name + str(self.entrydate)


