from django.http import JsonResponse
from ..models import invoice_collection
from ..models import invoice_collection
from ..models import survey_and_marketing_collection
from ..models import company_info_collection
from ..models import message_collection
from ..models import feedback_collection
from ..models import template_collection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpRequest
from rest_framework import status
import requests
import json
from bson.json_util import dumps
from cryptography.fernet import Fernet
from datetime import datetime
import datetime as dt



@api_view(['POST'])
def save_template(request :HttpRequest):
    
    request_body = json.loads(request.body)

    request_body['template_id'] = 1

    template = template_collection.find({'template_id': request_body['template_id']})

    if not list(template):
        template_collection.insert_one(request_body)
    else:
        template_collection.replace_one(filter={'template_id': request_body['template_id']}, replacement=request_body)

    return JsonResponse({'message': 'Changes are saved'},status=status.HTTP_200_OK, safe=False)


@api_view(['GET'])
def get_template_with_details(request :HttpRequest):

    id = request.GET['id']
    api = request.GET['api']
    

    template = template_collection.find_one({'template_id': 1})
    
    template_dump = dumps(template, indent = 2)  
    template_json = json.loads(template_dump)

    if  len(id) != 0 and template_json :
        invoice = invoice_collection.find_one({"invoice_number": id, 'api': api})
    
        invoice_dump = dumps(invoice, indent = 2)  
        invoice_json = json.loads(invoice_dump)

        template_json.update({'invoice':invoice_json})
        
        feedback = feedback_collection.find_one({"invoice_fk":id})
        feedback_dump = dumps(feedback, indent = 2)  
        feedback_json = json.loads(feedback_dump)
        print(feedback_json)

        if not feedback_json:
            template_json.update({'feedback':{}})
        else:
            template_json.update({'feedback':feedback_json})


    print(template_json)

    return JsonResponse(template_json, status=status.HTTP_200_OK, safe=False)