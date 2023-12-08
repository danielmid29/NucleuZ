from django.http import JsonResponse
from ..models import invoice_collection
from ..models import survey_and_marketing_collection
from ..models import company_info_collection
from ..models import message_collection
from ..models import template_collection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpRequest
from rest_framework import status
import json
from datetime import datetime
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from bson.json_util import dumps

import os

from telesign.messaging import MessagingClient

def send_invoice(invoices):
    
    
    template = template_collection.find_one({'template_id': 1})
    
    template_dump = dumps(template, indent = 2)  
    template_json = json.loads(template_dump)


    for invoice in invoices:
        url = f"http://nucleuz.s3-website.ap-south-1.amazonaws.com/invoice?id={invoice['invoice_number']}&at={invoice['api']}"
        message = 'This is your message'


    

        customer_id = os.getenv('CUSTOMER_ID', 'D8E4D314-14EF-436C-BBB5-C181CB4CF780')
        api_key = os.getenv('API_KEY', 'Ts/L7qVz8wSHerD5CZOO2segTYNsP6zMw/WzhdBxaAgGA0hu6dBphQ1UjOsVZlFL5dmLWR7ekMpR2alx44l8MA==')
        phone_number = os.getenv('PHONE_NUMBER', '918608003636')

        message = f"Your package {invoice['customer_name']} test {url}"
        message_type = "ARN"
        print(customer_id, api_key)
        
        messaging = MessagingClient(customer_id, api_key)

        response = messaging.message(phone_number, message, message_type)


        response_body = json.loads(response.body)
        
        contact = ''
        for contact_list in invoice['contact_persons_details']:
            if contact_list['mobile'] != '':
                contact = contact_list['mobile']
                invoice['contact'] = contact
                break


        if response_body['status']['code'] == 290:
            message={
                'reference_id': response_body['reference_id'],
                'invoice_id': invoice['invoice_number'],
                'billed_to': invoice['customer_name'], 
                'contact': contact,
                'status': 'QUEUED',
                'message': f"Your package{invoice['customer_name']} test {url}",
                'date': datetime.now()
            }

            message_collection.insert_one(message)
        else:
            message={
                'reference_id': response_body['reference_id'],
                'invoice_id': invoice['invoice_number'],
                'billed_to': invoice['customer_name'],
                'contact': contact,
                'status': 'Failed',
                'message': f"Your package {invoice['customer_name']} test {url}",
                'error': response_body['status']['description'],
                'date': datetime.now()
            }

            message_collection.insert_one(message)

        return invoices
    # return Response({"message":"Message has been queued and will soon be delivered"},status=status.HTTP_200_OK)





