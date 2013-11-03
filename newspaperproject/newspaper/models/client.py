from django.db import models

import datetime
from datetime import date

from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.db.models import F

class Client(models.Model):
  FREQ = (
      (1, 'Month'), 
      (2, 'Bimonth'), 
      (3, 'Quarter'), 
      (4, 'Biyear'), 
      (5, 'Year')
  )

  PREPAY = (
      (0, 'Nee'),
      (1, 'Ja')
  )
  
  name = models.CharField('Naam', max_length=255)
  firstname = models.CharField('Voornaam', max_length=255)
  street = models.CharField('Straat', max_length=255)
  number = models.CharField('Nummer', max_length=255)
  box = models.CharField('Bus', max_length=255, blank=True)
  pc = models.CharField('Postcode', max_length=255)
  city = models.CharField('Gemeente', max_length=255)
  round_nbr = models.IntegerField('Ronde')
  order = models.IntegerField('Volgorde in ronde')
  delivery_begindate = models.DateField('Levering Begindatum')
  delivery_enddate = models.DateField('Levering Einddatum')
  prepay = models.IntegerField('Vooraf betaler', choices=PREPAY)
  freq = models.IntegerField('Frequentie', choices=FREQ)
  saldo = models.FloatField()

  class Meta:
    app_label = 'newspaper'
    verbose_name = 'Klant'
    verbose_name_plural = 'Klanten'

  def isActive(self, client, entrydate):

    if client.delivery_begindate <= entrydate and client.delivery_enddate >= entrydate:
      return True
    else:
      return False
  
  def __repr__(self):
    return self.getString()

  def __str__(self):
    return self.getString()

  def getString(self):
    return str(self.id) + ': ' + self.name + ' ' + self.firstname

  def getActiveClients(self, entrydate = datetime.datetime.now()):
    return Client.objects.filter(
          delivery_begindate__lte = entrydate
        ).filter(
          delivery_enddate__gte = entrydate    
        ).order_by(
          'round_nbr', 'order'
        ).all()

  def isNewOrderNumber(self, clientId, orderNumber, roundNumber):
    client = Client.objects.all().filter(order = orderNumber, round_nbr = roundNumber).exclude(id = clientId)

    if client:
      return True
    else:
      return False

  def updateOrderNumber(self, orderNumber, roundNumber):
    Client.objects.all().filter(order__gte = orderNumber, round_nbr = roundNumber).update(order = F('order') + 1)

  def _getBoxNumber(self):
    
    if self.box == '0':
      return ''
    
    return self.box

  box_number = property(_getBoxNumber)

@receiver(pre_save, sender=Client)
def updateRoundOrder(sender, **kwargs):
  client = kwargs['instance']

  if client.isNewOrderNumber(client.id, client.order, client.round_nbr):
    client.updateOrderNumber(client.order, client.round_nbr)
