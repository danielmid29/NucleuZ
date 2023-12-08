from django.db import models
from mongo_config import db

class Invoice(models.Model):
    invoice_id = models.CharField(max_length=200)
    billed_to = models.CharField(max_length=500)

    def __str__(self) -> str:
        return self.invoice_id + " " + self.billed_to
    


invoice_collection = db['invoices']
survey_and_marketing_collection = db['survey_and_marketing']
company_info_collection = db['company_info']
message_collection = db['message']
feedback_collection = db['feedback']
api_collection = db['invoice_api']
template_collection = db['template']