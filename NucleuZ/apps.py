from django.apps import AppConfig

class NucleuzConfig(AppConfig):
    name = 'NucleuZ'

    def ready(self):
        from .services import send_invoice

        send_invoice.runScheduler()