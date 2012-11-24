from django.template import Context, loader
from django.shortcuts import render
from django.http import HttpResponse
from invoice import InvoiceForm

def index(request):
  return HttpResponse("Index pagina")

def invoice(request):
  form = InvoiceForm()

  t = loader.get_template('admin/change_form.html')
  c = Context({'form': form,})
  return HttpResponse(t.render(c))
