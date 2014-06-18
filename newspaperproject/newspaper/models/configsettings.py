from django.db import models

class ConfigSettings(models.Model):
  name = models.CharField('Naam', max_length=255)
  value = models.CharField('Waarde', max_length=255)

  def __str__(self):
    return str(self.name)

  class Meta:
    app_label = 'newspaper'
    verbose_name = 'Configuratie'
    verbose_name_plural = 'Configuraties'


