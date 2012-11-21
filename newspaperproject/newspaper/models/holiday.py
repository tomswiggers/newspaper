from django.db import models
from newspaper.models import Client

import datetime
from datetime import date

class Holiday(models.Model):
  begindate = models.DateField()
  enddate = models.DateField()
  client = models.ForeignKey(Client)

  class Meta:
    app_label = "newspaper"
    ordering = ['-begindate']

  def __str__(self):
    return str(self.client.id) + ': ' + self.client.firstname + ' ' + self.client.name + ' ' + str(self.begindate) + ' -> ' + str(self.enddate)

  def __repr__(self):
    return str(self.client_id) + ' ' + str(self.begindate) + ' ' + str(self.enddate)

  def saveHoliday(clientId, begin, end):
    this.client_id = clientId
    this.begindate = begin
    this.enddate = end

    this.save()
