from django.db import models
from newspaper.models import Client
from newspaper.models import Item

import datetime
from datetime import date

class Delivery(models.Model):
  client = models.ForeignKey(Client)
  item = models.ForeignKey(Item)
  days = models.IntegerField()
  begindate = models.DateField()
  enddate = models.DateField()
  
  class Meta:
    app_label = 'newspaper'
    ordering = ['client']
    verbose_name = 'Levering'
    verbose_name_plural = 'Leveringen'

  def __str__(self):
    return str(self.client.id) + ': ' + self.client.firstname + ' ' + self.client.name + ' ' + self.item.name + '(' + str(self.begindate) + ' -> ' + str(self.enddate) + ')'


