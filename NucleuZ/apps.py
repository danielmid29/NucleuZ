from django.apps import AppConfig



running = False

class NucleuzConfig(AppConfig):
    name = 'NucleuZ'

    def ready(self):
        global running
        from .services import invoice_api
        print('outside')
        if(running == False):
            
            print('inside')
            running = invoice_api.runScheduler()