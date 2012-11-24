from django import forms

class InvoiceForm(forms.Form):
  date = forms.DateField()
