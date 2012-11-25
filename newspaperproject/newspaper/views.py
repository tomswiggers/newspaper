import os
import datetime
import shutil

from django.template import Context, Template, loader, RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.http import HttpResponse
from forms import InvoiceForm
from invoice import Invoice

def index(request):
  return HttpResponse("Index pagina")

def invoice(request):

  if request.method == 'POST':

    form = InvoiceForm(request.POST)

    if form.is_valid():
      month = request.POST['month']

      invoice = Invoice(2012, int(month))
      invoice.calculateInvoice()

      return render_to_response('invoice-success.html', {'listName': invoice.getListFilename(), 'invoiceName': invoice.getInvoiceFilename()}, context_instance=RequestContext(request))
    else:
      return HttpResponse('Invalid form data.' + str(form))

  form = InvoiceForm()
  return render_to_response('invoice.html', {'form': form}, context_instance=RequestContext(request))

def backup(request):
  path = os.path.realpath(os.path.dirname(__file__))
  dbFullFilename = path + '/../newspaper.db'

  backupFilename = 'newspaper-' + str(datetime.datetime.now()) + '.db' 
  backupFullFilename = path + '/static/' + backupFilename

  shutil.copy(dbFullFilename, backupFullFilename)

  return render_to_response('backup.html', {'backupFilename': backupFilename}, context_instance=RequestContext(request))
