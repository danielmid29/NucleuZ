from django.apps import AppConfig

class NucleuzConfig(AppConfig):
    name = 'NucleuZ'

    def ready(self):
        from .services import invoice_api

        invoice_api.runScheduler()