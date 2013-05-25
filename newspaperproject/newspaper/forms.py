from django import forms
from django.contrib.admin import widgets

from newspaper.models import *

class DatePickerForm(forms.Form):
  months = (
    ('1', 'Januari'),
    ('2', 'Februari'),
    ('3', 'Maart'),
    ('4', 'April'),
    ('5', 'Mei'),
    ('6', 'Juni'),
    ('7', 'July'),
    ('8', 'Augustus'),
    ('9', 'September'),
    ('10', 'Oktober'),
    ('11', 'November'),
    ('12', 'December')
  )

  years = (
    ('2013', '13'),
    ('2014', '14'),
    ('2015', '15'),
  )

  year = forms.ChoiceField(label='Factuur jaar', choices=years)
  month = forms.ChoiceField(label='Factuur maand', choices=months)
  client = forms.IntegerField(label='Klant nummer')
