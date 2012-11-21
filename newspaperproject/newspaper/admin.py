from newspaper.models import Client
from newspaper.models import Holiday
from newspaper.models import BankHoliday
from newspaper.models import Delivery
from newspaper.models import Item
from newspaper.models import Price

from django.contrib import admin

class ClientAdmin(admin.ModelAdmin):
  list_filter = ('round_nbr',)
  search_fields = ('id', 'name', 'firstname')

admin.site.register(Client, ClientAdmin)
admin.site.register(Holiday)
admin.site.register(BankHoliday)
admin.site.register(Delivery)
admin.site.register(Item)
admin.site.register(Price)
