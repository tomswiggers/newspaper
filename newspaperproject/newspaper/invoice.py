import datetime
import time
import os, sys
 
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

from django.db import models
from django.core.management import call_command
from django.db import connection

from newspaper.models import *

from configmerchant import ConfigMerchant

from django.conf import settings

class Invoice:

  MONTH = 1
  BIMONTH = 2
  QUARTER = 3
  BIYEAR = 4
  YEAR = 5


  def __init__(self, year, month):
    self.year = year
    self.month = month

    self.beginDate = datetime.date(year, month, 1)
    self.endDate = self.getEndDateMonth(self.beginDate)

  def log(self, msg):
    timestamp = datetime.datetime.now()
    print timestamp.isoformat() + ': ' + str(msg)

  def getListFilename(self):
    return 'betalingslijst-' + str(self.beginDate.strftime('%B')) + '.csv'

  def getInvoiceFilename(self):
    return 'facturen-' + str(self.beginDate.strftime('%B')) + '.txt'

  def getInvoiceFullFilename(self):
    return os.path.realpath(os.path.dirname(__file__)) + '/static/' + self.getInvoiceFilename()

  def getListFullFilename(self):
    return os.path.realpath(os.path.dirname(__file__)) + '/static/' + self.getListFilename()

  def getLastDayOfMonth(self, date):
    nextMonth = (date.month % 12) + 1
    lastDay = datetime.date(date.year, nextMonth, 1) - datetime.timedelta(days = 1)

    return lastDay.day

  def getEndDateMonth(self, entryDate):
    return datetime.date(entryDate.year, entryDate.month, self.getLastDayOfMonth(entryDate))

  def getEndDateNextMonth(self, entryDate):
    beginDateNextMonth = self.getBeginDateNextMonth(entryDate)
    return datetime.date(beginDateNextMonth.year, beginDateNextMonth.month, self.getLastDayOfMonth(beginDateNextMonth))

  def getBeginDatePreviousMonth(self, entryDate):
    month = entryDate.month - 1

    if month == 0:
      month = 12
      year = entryDate.year - 1
    else:
      year = entryDate.year

    return datetime.date(year, month, 1)

  def getBeginDateNextMonth(self, entryDate):
    month = (entryDate.month % 12) + 1

    if month == 1:
      year = entryDate.year + 1
    else:
      year = entryDate.year

    return datetime.date(year, month, 1)

  def getEndDateQuarter(self, entryDate):

    for i in [1,2,3]:
      entryDate = self.getEndDateNextMonth(entryDate)

    return entryDate

  def getClients(self):
    return Client.objects.order_by('round_nbr', 'order').all()

  def getClientsWithSaldo(self):
    return Client.objects.filter(saldo__gt=0).all()

  def calculateInvoice(self):
    invoices = self.getInvoiceList(self.getClients())

    self.writeList(invoices)
    self.writeInvoices(invoices)

  def calculateSaldos(self):
    clients = self.getClientsWithSaldo()
    invoices = self.getInvoiceList(clients)

    return self.processSaldos(invoices)

  def getInvoiceList(self, clients):
    self.log('Start')
    invoices = list()
       
    for client in clients:
      flag = True
      self.log('Start getInvoice: ' + str(client))

      beginDate = self.beginDate
      endDate = self.endDate

      if client.prepay == 1:

        if client.freq == self.MONTH:
          print "===== PREPAY MONTH ====="
          beginDate = self.getBeginDateNextMonth(beginDate)
          endDate = self.getEndDateMonth(beginDate)
        elif client.freq == self.QUARTER and beginDate.month % 3 == 0:
          print "===== PREPAY QUARTER ====="
          beginDate = self.getBeginDateNextMonth(beginDate)
          endDate = self.getEndDateQuarter(endDate)
        else:
          print "===== PREPAY NOK ====="
          flag = False
      else:

        if client.freq == self.BIMONTH:
          
          if beginDate.month % 2 == 0:
            beginDate = self.getBeginDatePreviousMonth(beginDate)
          else:
            flag = False

      if flag:
        invoices.append(self.getInvoice(client, beginDate, endDate))

      self.log('End getInvoice: ' + str(client))

    return invoices

  def getInvoice(self, client, beginDate, endDate):
    flag = True
    invoices = dict()

    currentDate = beginDate

    deliveries = self.getDeliveries(client.id)
    holidays = self.getHolidays(client.id)
    bankHolidays = self.getBankHolidays()
    deliveryExceptions = self.getDeliveryExceptions(beginDate, endDate)

    while currentDate <= endDate:

      #check if client has a holiday
      if self.isHoliday(holidays, currentDate):
        flag = False

      #check if it's a bank holiday
      if self.isBankHoliday(bankHolidays, currentDate):
        flag = False

      #check if client is active
      if not client.isActive(client, currentDate):
        flag = False

      if flag:
        invoicesPerDay = self.processDeliveries(client, deliveries, currentDate)
        
        for invoicePerDay in invoicesPerDay:
    
          #check if there is a delivery exception
          if not self.isDeliveryException(deliveryExceptions, currentDate, invoicePerDay['item']):

            #check client already in invoice list
            if not invoices.has_key(client.id):
              invoices[client.id] = {'client': client, 'deliveries': {}, 'beginDate': beginDate, 'endDate': endDate}

            #check if price is already in delivery list for client
            if not invoices[client.id]['deliveries'].has_key(invoicePerDay['price'].id):
              invoices[client.id]['deliveries'][invoicePerDay['price'].id] = {'total': 1, 'price': invoicePerDay['price'], 'item': invoicePerDay['item']}
            else:
              flagMonthly = False
              flagBiWeekly = False

              #Add monthly items only once per month
              if self.isMonthlyItemAlreadyInList(invoices[client.id]['deliveries'][invoicePerDay['price'].id]):
                flagMonthly = True

              #Add bi-weekly items only once per week
              if self.isWeeklyItemAlreadyInList(invoices[client.id]['deliveries'][invoicePerDay['price'].id], currentDate):
                flagBiWeekly = True

              if not flagMonthly and not flagBiWeekly:
                invoices[client.id]['deliveries'][invoicePerDay['price'].id]['total'] = invoices[client.id]['deliveries'][invoicePerDay['price'].id]['total'] + 1
                invoices[client.id]['deliveries'][invoicePerDay['price'].id]['item'].weekNumber = self.getWeekNumber(currentDate)

      flag = True
      currentDate = currentDate + datetime.timedelta(days = 1)

    return invoices

  def isDeliveryException(self, deliveryExceptions, currentDate, item):

    for deliveryException in deliveryExceptions:
      
      if deliveryException.item.id == item.id and deliveryException.entrydate == currentDate:
        return True
    
    return False

  def isMonthlyItemAlreadyInList(self, delivery):

    if delivery['item'].freq == 4:
      return True
    else:
      return False

  def isWeeklyItemAlreadyInList(self, delivery, currentDate):
    
    if delivery['item'].freq == 3:
      weekNumber = self.getWeekNumber(currentDate)

      if weekNumber == delivery['item'].weekNumber:
        return True
      else:
        print "add item"
        return False
    else:
      return False

  def getDeliveries(self, clientId):
    deliveries = list()

    query = Delivery.objects
    query = query.filter(client_id=clientId)

    return query.all()

  def isDeliveryForMonth(self, delivery, begindate, enddate):
    delta = datetime.timedelta(days=1)
    entrydate = begindate

    while entrydate <= enddate:
      
      if entrydate >= delivery.begindate and entrydate <= delivery.enddate:
        return True
      else:
        entrydate = entrydate + delta

    return False

  def getHolidays(self, clientId):
    return Holiday.objects.filter(client_id = clientId).all()

  def getBankHolidays(self):
    return BankHoliday.objects.all()

  def getDeliveryExceptions(self, beginDate, endDate):
    return DeliveryException.objects.filter(entrydate__gte=beginDate, entrydate__lte=endDate).all()

  def isHoliday(self, holidays, currentDate):

    for holiday in holidays:

      if holiday.begindate <= currentDate and holiday.enddate >= currentDate:
        return True

    return False  

  def isBankHoliday(self, holidays, currentDate):

    for holiday in holidays:

      if holiday.entrydate == currentDate:
        return True

    return False  

  def processDeliveries(self, client, deliveries, currentDate):
    invoices = list()

    for delivery in deliveries:

      if currentDate >= delivery.begindate and currentDate <= delivery.enddate:
        
        if (delivery.days > 0):

          if Item().isDeliveryDay(currentDate, delivery.days):
            item = self.getItem(delivery.item_id)
            price = self.getPrice(delivery.item_id, currentDate)
            invoices.append({'price': price, 'item': item, 'currentDate': currentDate})
        else:
          item = self.getItem(delivery.item_id)

          if item.freq == 2:

            if Item().isDeliveryDay(currentDate, item.days):
              price = self.getPrice(delivery.item_id, currentDate)
              invoices.append({'price': price, 'item': item, 'currentDate': currentDate})
          elif item.freq == 3:

            if self.getWeekNumber(currentDate) % 2 == 0:
              price = self.getPrice(delivery.item_id, currentDate)
              item.weekNumber = self.getWeekNumber(currentDate)
              invoices.append({'price': price, 'item': item, 'currentDate': currentDate})
          elif item.freq == 4:
            price = self.getPrice(delivery.item_id, currentDate)
            invoices.append({'price': price, 'item': item, 'currentDate': currentDate})
          else:
            print '------------------------Other freq-----------------------------'

    return invoices

  def getItem(self, itemId):
    return Item.objects.filter(id = itemId).get()
  
  def getPrice(self, itemId, currentDate):
    query = Price.objects
    query = query.filter(item_id=itemId, begindate__lte=currentDate, enddate__gte=currentDate)

    return query.get()

  def processSaldos(self, invoices):
    saldos = list()

    for invoice in invoices:

      if len(invoice.values()) > 0:
        total = self.getTotal(invoice.values()[0])
        client = invoice.values()[0]['client']

        pay = float(0)
        saldoNew = float(0)

        if client.saldo > total:
          pay = 0
          saldoNew = client.saldo - total
        else:
          pay = total - client.saldo
          saldoNew = 0

        saldos.append({'id': client.id, 'name': client.name, 'saldo': client.saldo, 'total': total, 'pay': pay, 'saldoNew': saldoNew})

    return saldos

  def printSaldos(self, invoices):
    line = "{:<5}{:<30}{:>15}{:>25}{:>25}{:>15}"
  
    print line.format("Id", "Naam", "Vorig saldo", "Bedrag " + str(self.beginDate.strftime('%B')), "Te betalen " + str(self.beginDate.strftime('%B')), "Nieuw saldo")

    for invoice in invoices:

      if len(invoice.values()) > 0:
        total = self.getTotal(invoice.values()[0])
        client = invoice.values()[0]['client']

        pay = float(0)
        saldoNew = float(0)

        if client.saldo > total:
          pay = 0
          saldoNew = client.saldo - total
        else:
          pay = total - client.saldo
          saldoNew = 0

        print line.format(client.id, client.name, client.saldo, total, pay, saldoNew)

  def writeList(self, invoices):
    print '------------------writeList--------------------'
    line = '{};{};{};{};{};{};{}\n'
    filename = self.getListFullFilename()
    fp = open(filename, 'w')

    fp.write('Postcode;Gemeente;Straat;Nummer;Naam;Voornaam;Totaal\n')
    
    for client in self.sortInvoiceList(invoices):
      fp.write(line.format(client['pc'], client['city'], client['street'], client['number'], client['name'], client['firstname'], client['total']))

  def sortInvoiceList(self, invoices):
    invoiceList = list()

    for invoice in invoices:

      if len(invoice.values()) > 0:
        invoiceList.append(self.getClientSummary(invoice.values()[0]))

    return sorted(invoiceList, key=lambda k: (k['pc'], k['street'].lower(), int(k['number'])))

  def writeInvoices(self, invoices):
    filename = self.getInvoiceFullFilename()
    fp = open(filename, 'w')

    for invoice in invoices:

      if len(invoice.values()) > 0:
        fp.write(self.getClientInvoice(invoice.values()[0]))

  def getTotal(self, invoice):
    total = float(0)

    for priceId in invoice['deliveries']:
      total = total + (invoice['deliveries'][priceId]['price'].price * invoice['deliveries'][priceId]['total'])
    
    return total

  def getClientSummary(self, invoice):
    total = self.getTotal(invoice)

    client = invoice['client']
    
    if total < client.saldo:
      total = 0
    elif total > client.saldo and client.saldo > 0:
      total = total - client.saldo

    return {'pc': client.pc, 'city': client.city, 'street': client.street, 'number': client.number, 'name': client.name, 'firstname': client.firstname, 'total': total}

  def getClientInvoice(self, invoice):
    client = invoice['client']
    deliveries = invoice['deliveries']

    if sys.platform.startswith('linux'):
      delimiter = '\r\n'
    else:
      delimiter = '\n'

    if not client.box == "0":
      houseNumber = client.number + '/' + client.box
    else:
      houseNumber = client.number

    invoiceStr = delimiter
    invoiceStr = invoiceStr + delimiter
    invoiceStr = invoiceStr + ConfigMerchant.line1 + delimiter
    invoiceStr = invoiceStr + ConfigMerchant.line2 + delimiter
    invoiceStr = invoiceStr + ConfigMerchant.line3 + delimiter
    invoiceStr = invoiceStr + ConfigMerchant.line4 + datetime.date.today().isoformat() + delimiter
    invoiceStr = invoiceStr + '__________________________________________________________________________' + delimiter
    invoiceStr = invoiceStr + 'REKENING van ' + invoice['beginDate'].isoformat() + ' tot ' + invoice['endDate'].isoformat() + '             ' + client.name + ' ' + client.firstname + delimiter
    invoiceStr = invoiceStr + '                                                   ' + client.street + ' ' + houseNumber + delimiter
    invoiceStr = invoiceStr + '                                                   ' + client.pc + ' ' + client.city + delimiter

    invoiceStr = invoiceStr + delimiter
    invoiceStr = invoiceStr + 'omschrijving                aantal               prijs              totaal' + delimiter
    invoiceStr = invoiceStr + '__________________________________________________________________________' + delimiter

    total = float(0)
    counter = 0

    for priceId in deliveries:
      counter = counter + 1
      totalItem = float(deliveries[priceId]['total']) * float(deliveries[priceId]['price'].price)
      total = total + totalItem
      invoiceStr = invoiceStr + "%-28s%-21s%-20s%5s" % (deliveries[priceId]['item'].description, str(deliveries[priceId]['total']), str(float(deliveries[priceId]['price'].price)), str(totalItem))
      invoiceStr = invoiceStr + delimiter

    while counter < 6:
      invoiceStr = invoiceStr + delimiter
      counter = counter + 1

    invoiceStr = invoiceStr + '__________________________________________________________________________' + delimiter
    invoiceStr = invoiceStr + 'TOTALEN:                                                         %.2f EUR' % (total)
    invoiceStr = invoiceStr + delimiter + delimiter

    #check prepay and saldo
    if client.saldo > 0:

      if client.saldo - total < 0:
        remaining = total - client.saldo
      else:
        remaining = float(0)

      invoiceStr = invoiceStr + 'VOORSCHOT:                                                     %.2f EUR' % (total)
      invoiceStr = invoiceStr + delimiter
      invoiceStr = invoiceStr + 'SALDO:                                                         %.2f EUR' % (client.saldo - total)
      invoiceStr = invoiceStr + delimiter
      invoiceStr = invoiceStr + 'TE BETALEN:                                                    %.2f EUR' % (remaining)
      invoiceStr = invoiceStr + delimiter

    invoiceStr = invoiceStr + delimiter
    invoiceStr = invoiceStr + 'Maandagnamiddag en zaterdagnamiddag gesloten  !!!' + delimiter
    invoiceStr = invoiceStr + 'Gelieve de rekening in de winkel te betalen.' + delimiter
    invoiceStr = invoiceStr + delimiter
    invoiceStr = invoiceStr + delimiter
    invoiceStr = invoiceStr + delimiter

    if client.saldo == 0:
      invoiceStr = invoiceStr + delimiter
      invoiceStr = invoiceStr + delimiter
      invoiceStr = invoiceStr + delimiter

    invoiceStr = invoiceStr + delimiter
    invoiceStr = invoiceStr + delimiter
    invoiceStr = invoiceStr + delimiter
    invoiceStr = invoiceStr + delimiter

    return invoiceStr

  def getWeekNumber(self, entryDate):
    currentDate = datetime.date(entryDate.year, entryDate.month, 1)
    delta = datetime.timedelta(days=1)
    counter = 1

    while currentDate <= entryDate:

      if (currentDate.weekday()+1) % 7 == 1 and currentDate.day > 3:
        counter = counter + 1
        
      currentDate = currentDate + delta

    return counter
