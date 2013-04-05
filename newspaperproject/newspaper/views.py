import os
import datetime
import shutil

from django.template import Context, Template, loader, RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse
from forms import DatePickerForm
from invoice import Invoice

from newspaper.models import *

def index(request):
  return HttpResponse("Index pagina")

def invoice(request):

  if request.method == 'POST':
    form = DatePickerForm(request.POST)

    if form.is_valid():
      month = request.POST['month']
      year = request.POST['year']
      clients = request.POST['clients']

      if clients:
        clients = Client.objects.filter(pk=clients)
      else:
        clients = None

      invoice = Invoice(int(year), int(month))
      invoice.calculateInvoice(clients)

      return render_to_response('invoice-success.html', {'listName': invoice.getListFilename(), 'invoiceName': invoice.getInvoiceFilename()}, context_instance=RequestContext(request))
    else:
      return HttpResponse('Invalid form data.' + str(form))

  form = DatePickerForm()
  return render_to_response('invoice.html', {'form': form}, context_instance=RequestContext(request))

def backup(request):
  path = os.path.realpath(os.path.dirname(__file__))
  dbFullFilename = path + '/../newspaper.db'

  backupFilename = 'newspaper-' + str(datetime.datetime.now()) + '.db' 
  backupFullFilename = path + '/static/' + backupFilename

  shutil.copy(dbFullFilename, backupFullFilename)

  return render_to_response('backup.html', {'backupFilename': backupFilename}, context_instance=RequestContext(request))

def calculateSaldos(request):

  if request.method == 'POST':
    form = DatePickerForm(request.POST)

    if form.is_valid():
      month = request.POST['month']
      year = request.POST['year']

      invoice = Invoice(int(year), int(month))
      invoices = invoice.calculateSaldos()

      clientFormSet= modelformset_factory(Client)

    return render_to_response('saldos.html', {'invoices': invoices, 'title': 'Saldos'}, context_instance=RequestContext(request))
  else:
    form = DatePickerForm()
    return render_to_response('date-picker.html', {'form': form, 'formAction': '/admin/newspaper/saldos/', 'title': 'Saldos'}, context_instance=RequestContext(request))

def clientList(request):
  client = Client()
  clientList = client.getActiveClients()

  line = '{};{};{};{};{};{};{};{}\n'
  filename = self.getListFullFilename()
  fp = open(filename, 'w')

  fp.write('Postcode;Gemeente;Straat;Nummer;Bus;Naam;Voornaam;Totaal\n')

  for client in self.sortInvoiceList(invoices):
    fp.write(line.format(client['pc'], client['city'], client['street'], client['number'], client['box'], client['name'], client['firstname'], client['total']))

  return render_to_response('success.html', {'fileName': filename}, context_instance=RequestContext(request))
