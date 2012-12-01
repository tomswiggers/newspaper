from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/newspaper/invoice/', 'newspaper.views.invoice'),
    url(r'^admin/newspaper/saldos/', 'newspaper.views.calculateSaldos'),
    url(r'^admin/newspaper/backup/', 'newspaper.views.backup'),
    url(r'^admin/', include(admin.site.urls)),
)
