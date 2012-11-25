from django import forms
from django.contrib.admin import widgets

class InvoiceForm(forms.Form):
  months = (
    ('11', 'November'),
    ('12', 'December')
  )

  years = (('2012', '12'))

  month = forms.ChoiceField(label='Factuur maand', choices=months)
