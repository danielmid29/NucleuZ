from django.http import JsonResponse
from ..models import invoice_collection
from ..models import invoice_collection
from ..models import survey_and_marketing_collection
from ..models import company_info_collection
from ..models import message_collection
from ..models import api_collection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpRequest
from rest_framework import status
import requests
import json
from bson.json_util import dumps
from cryptography.fernet import Fernet
from .send_invoice import send_invoice
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from bson import ObjectId
import base64

access_token=""
time : datetime = datetime.now()
lrt=""


key = Fernet.generate_key()
cipher_suite = Fernet(key)

def get_access_token(client_id, client_secret, code, nrt, cpt):
    global lrt
    global access_token

    redirect_uri = 'http://127.0.0.1:8000/'
    grant_type= 'authorization_code'

    auth_url = 'https://accounts.zoho.in/oauth/v2/token'

    response :requests.Response
    try:
        if nrt:            
            fernet = Fernet(bytes(cpt,'UTF-8'))
            client_id  = fernet.decrypt(bytes(client_id, 'UTF-8')).decode()
            client_secret  = fernet.decrypt(bytes(client_secret, 'UTF-8')).decode()
            nrt  = fernet.decrypt(bytes(nrt, 'UTF-8')).decode()


            payload = {'client_id':client_id , 'client_secret':client_secret, 'refresh_token':nrt, 'grant_type':'refresh_token' }
            response = requests.post(auth_url, data=payload)
            
            data = json.loads(response.text)
            if('error'  in response.text):
                print(f"error while getting access token : {response.text}")
                if('error_description'  in response.text):
                    raise Exception(data['error']+ f'({data["error_description"]})')
                else:
                    raise Exception(data['error'])
        else:
            payload = {'client_id':client_id , 'client_secret':client_secret, 'redirect_uri':redirect_uri,'code':code, 'grant_type': grant_type}
            response = requests.post(auth_url, data=payload)
            
            data = json.loads(response.text)
            if('error'  in response.text):
                print(f"error while getting access token : {response.text}")
                if('error_description'  in response.text):
                    raise Exception(data['error']+ f'({data["error_description"]})')
                else:
                    raise Exception(data['error'])

            
            
            lrt = data['refresh_token']
    except requests.exceptions.HTTPError as err:
        print(f"error while getting access token : http {err.strerror}")
        raise Exception(f"error while getting access token : http {err.strerror}")
    except Exception as err:
        print(f"error while getting access token : {err}")
        raise  Exception(f"error while getting access token : {err}")
        
    data = json.loads(response.text)
    access_token = data['access_token']
    time = datetime.now()




def get_invoice_data_api(id, api_json, retry :bool, invoice_id_sep):

    current_time = datetime.now()
    difference = current_time - time

    print(difference.total_seconds())

    if access_token == "" or difference.total_seconds() > 3600 :
        try:
            get_access_token(api_json['client_id'],api_json['client_secret'],api_json['scope_code'],api_json['nrt'],api_json['cpt'] )
        except Exception as e:
            print(e)
            raise Exception(f"S{e}")

    

    response :requests.Response


    try:
        headers = {"Authorization": f"Zoho-oauthtoken {access_token}", "X-com-zoho-invoice-organizationid":api_json['organization_id']}

        invoice_id : str = ''
        print('invoice_id_sep',invoice_id_sep)
        if invoice_id_sep: 
            invoice_id = invoice_id_sep
        else:
            
            print('invoice_id_sep inside',invoice_id_sep)
            response = requests.get(f"https://www.zohoapis.in/invoice/v3/invoices/", headers=headers)
            data = json.loads(response.text)

            if data['code'] != 0:
                print('error')
                raise Exception(data['message'])
                print(data)
                
            invoices = data['invoices']



            if id == '':
                return data
            
            for invoice in invoices:
                if invoice['invoice_number'] == id:
                    print(invoice['invoice_id'])
                    invoice_id = invoice['invoice_id']
                else: 
                    print('Not found')    

        if invoice_id :
            response = requests.get(f"https://www.zohoapis.in/invoice/v3/invoices/{invoice_id}", headers=headers)
        else:
            raise Exception('Resource not found')
    except requests.exceptions.HTTPError as e: 
        if e.response.status_code == 401 & retry:
            try:
                get_access_token(api_json['client_id'],api_json['client_secret'],api_json['scope_code'],api_json['irt'] )
            except Exception as e:
                print(e)
                raise Exception(f"{e}")
            get_invoice_data_api(id, False,'')
        else:
            raise Exception(f"error while getting invoice details : {e}")
    except Exception as e:
        if  'not found' in str(e):
            raise Exception(e)
        else:
            raise Exception(f"error while getting invoice details : {e}")
    
    data = json.loads(response.text)

    return data




@api_view(['GET'])
def get_invoice_details(request):
    
    

    id = request.GET['id']
    api = request.GET['api']

    api_data = api_collection.find_one({"api_name":api})
    api_json = json.loads(dumps(api_data))

    try:
        invoice_api_data = get_invoice_data_api(id, api_json, True, '')
    except Exception as e:
        if 'not found' in str(e):
            return JsonResponse({"error": str(e)}, status=status.HTTP_404_NOT_FOUND, safe=False)
        else:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
        
    invoice = invoice_collection.find_one({"invoice_number": id})

    if not invoice:
        return Response({"invoice":invoice_api_data}, status= status.HTTP_200_OK)
    else:    
        invoice_dump = dumps(invoice, indent = 2)  
        invoice_json = json.loads(invoice_dump)

        invoice_pk = ObjectId(invoice_json['_id']['$oid'])

        sam = survey_and_marketing_collection.find({"invoice_fk":invoice_pk})
        sam_list =  list(sam)
        sam_dump = dumps(sam_list, indent = 2)  
        sam_json = json.loads(sam_dump)

        company_info = company_info_collection.find({"invoice_fk":invoice_pk})
        company_info_list =  list(company_info)
        company_info_dump = dumps(company_info_list, indent = 2)  
        company_info_json = json.loads(company_info_dump)

        message = message_collection.find({"invoice_fk": invoice_pk})
        message_list =  list(message)
        message_dump = dumps(message_list, indent = 2)  
        message_json = json.loads(message_dump)
        
        for contact in invoice_api_data['invoice']['contact_persons_details']:
            if len(contact['mobile']) != 0:
                invoice_api_data['invoice']['contact'] = contact['mobile']
            if len(contact['email']) != 0:
                invoice_api_data['invoice']['email'] = contact['email']
       
        response = {
            "invoice":invoice_api_data,
            "survey_and_marketing":sam_json,
            "company_info":company_info_json,
            "message": message_json
        } 

    return JsonResponse(response, status=status.HTTP_200_OK, safe=False) 



def check_new_invoice():
    api_data = api_collection.find_one({"api_name":'ZOHO'})
    api_json = json.loads(dumps(api_data))


    try:
        invoice_api_data = get_invoice_data_api('', api_json, True,'')
    except Exception as e:
        if 'not found' in str(e):
            return JsonResponse({"error": str(e)}, status=status.HTTP_404_NOT_FOUND, safe=False)
        else:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)
        

    api_invoices = invoice_api_data['invoices']
    invoices = invoice_collection.find()

    invoices_list =  list(invoices)
    invoices_dump = dumps(invoices_list, indent = 2)  
    invoices_json = json.loads(invoices_dump)
    

    invoice_ids = []

    new_invoices = []

    for invoice in invoices_json:
        invoice_ids.append(invoice['invoice_number'])

    for api_invoice in api_invoices:
        if api_invoice['invoice_number'] in invoice_ids:
            print('Already Exist')
        else:
            print(api_invoice['invoice_number'])
            invoice_api_data = get_invoice_data_api(api_invoice['invoice_number'], api_json, True,api_invoice['invoice_id'])
            invoice_api_data['invoice'].update({'api':'ZOHO'})
            new_invoices.append(invoice_api_data['invoice'])

    if new_invoices:
        sent_invoices = send_invoice(new_invoices)
        invoice_collection.insert_many(sent_invoices)

    return JsonResponse({"error": 'str(e)'}, status=status.HTTP_204_NO_CONTENT, safe=False)



def runScheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_new_invoice, 'interval', seconds = 60)
    scheduler.start()
    return True

@api_view(['POST'])
def invoice_api(request: HttpRequest):
    
    global lrt
    request_body = json.loads(request.body)

    api_list = list(api_collection.find({"api_name": request_body['api_name']}))
    
    request_body['scope_code'] = str(cipher_suite.encrypt(request_body['scope_code'].encode()), 'UTF-8')
    request_body['client_id'] = str(cipher_suite.encrypt(request_body['client_id'].encode()), 'UTF-8')
    request_body['client_secret'] = str(cipher_suite.encrypt(request_body['client_secret'].encode()), 'UTF-8')
    request_body['nrt'] =str(cipher_suite.encrypt(lrt.encode()), 'UTF-8') 
    request_body['cpt'] = str(key, 'UTF-8')

    if not api_list:
        api_collection.insert_one(request_body)
    else:
        api_collection.replace_one({"api_name": request_body['api_name']}, replacement=request_body)

    lrt =''

    return Response({"message": "Api details are added"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def test_api(request: HttpRequest):
    request_body = json.loads(request.body)
    request_body['nrt'] = ''
    request_body['cpt'] = ''
    try:
        get_invoice_data_api(request_body['invoice_number'], request_body, True,'')
    except Exception as e:
        if 'not found' in str(e):
            return Response({"message": "Api is working good"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": 'Please provide valid API details'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR, safe=False)

    return Response({"message": "Api is working good"}, status=status.HTTP_200_OK)