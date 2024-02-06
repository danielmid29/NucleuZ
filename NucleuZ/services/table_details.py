from django.http import JsonResponse
from django.http import HttpRequest
from ..models import invoice_collection
from ..models import survey_and_marketing_collection
from ..models import company_info_collection
from ..models import customers_collection
from ..models import message_collection
from ..models import feedback_collection
from ..models import stores_collection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from bson.json_util import dumps
import math
from datetime import datetime
from django.core.mail import EmailMessage, get_connection, send_mail
from django.conf import settings
import random

@api_view(['GET'])
def get_invoices(request :HttpRequest):

    page_number = request.GET['page_number']
    limit = int(request.GET['limit'])
    search_value = request.GET['search_value']


    find_json = {"$or" : [{'invoice_number': {"$regex" : search_value}}, {'api_name': {"$regex" : search_value}}, 
                          {'billed_to': {"$regex" : search_value}}, {'contact': {"$regex" : search_value}}, 
                          {'email': {"$regex" : search_value}}, {'selled_by': {"$regex" : search_value}}] }

    print(search_value)
    data = invoice_collection.find(find_json).sort('_id', -1).skip(limit * (int(page_number) - 1)).limit(limit)

    total = invoice_collection.count_documents(find_json)

    data_list =  list(data)
    json_data = dumps(data_list, indent = 2)  
    print(json_data)
    if not data_list:
        return Response({"error":"no records found"}, status= status.HTTP_404_NOT_FOUND)
    else: 
        response = {
            "count" :total,
            "total_pages": math.ceil(total/limit),
            "invoice": json.loads(json_data)
        }
        return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
    

@api_view(['GET'])
def get_invoice_details(request, id):
    invoice = invoice_collection.find_one({"invoice_number": id})
    

    if not invoice:
        return Response({"error":"no records found"}, status= status.HTTP_404_NOT_FOUND)
    else:    
        invoice_dump = dumps(invoice, indent = 2)  
        invoice_json = json.loads(invoice_dump)

        invoice_pk = invoice['_id']

        sam = survey_and_marketing_collection.find({"invoice_fk":invoice_pk})
        sam_list =  list(sam)
        sam_dump = dumps(sam_list, indent = 2)  
        sam_json = json.loads(sam_dump)

        company_info = company_info_collection.find({"invoice_fk":invoice_pk})
        company_info_list =  list(company_info)
        company_info_dump = dumps(company_info_list, indent = 2)  
        company_info_json = json.loads(company_info_dump)

        message = message_collection.find({"invoice_fk":invoice_pk})
        message_list =  list(message)
        message_dump = dumps(message_list, indent = 2)  
        message_json = json.loads(message_dump)
        
        feedback = feedback_collection.find({"invoice_fk":id})
        feedback_list =  list(feedback)
        feedback_dump = dumps(feedback_list, indent = 2)  
        feedback_json = json.loads(feedback_dump)

        response = {
            "invoice":invoice_json,
            "survey_and_marketing":sam_json,
            "company_info":company_info_json,
            "message": message_json,
            "feedback": feedback_json
        } 

        return JsonResponse(response, status=status.HTTP_200_OK, safe=False) 
    

@api_view(['GET'])
def get_messages(request :HttpRequest):

    page_number = request.GET['page_number']
    limit = int(request.GET['limit'])
    search_value = request.GET['search_value']


    find_json = {"$or" : [{'invoice_id': {"$regex" : search_value}}, {'status': {"$regex" : search_value}}, 
                          {'message': {"$regex" : search_value}}] }

    print(search_value)
    data = message_collection.find(find_json).sort('_id', -1).skip(limit * (int(page_number) - 1)).limit(limit)

    total = message_collection.count_documents(find_json)

    data_list =  list(data)
    json_data = dumps(data_list, indent = 2)  
    print(json_data)
    if not data_list:
        return Response({"error":"no records found"}, status= status.HTTP_404_NOT_FOUND)
    else: 
        response = {
            "count" :total,
            "total_pages": math.ceil(total/limit),
            "message": json.loads(json_data)
        }
        return JsonResponse(response, status=status.HTTP_200_OK, safe=False)


@api_view(['GET', 'POST'])
def get_customers(request :HttpRequest):

    if request.method == 'GET':
        page_number = request.GET['page_number']
        limit = int(request.GET['limit'])
        search_value = request.GET['search_value']


        find_json = {"$or" : [{'customer_id': {"$regex" : search_value}}, {'customer_name': {"$regex" : search_value}}, 
                            {'contact': {"$regex" : search_value}}, 
                            {'email': {"$regex" : search_value}}] }

        print(search_value)
        data = customers_collection.find(find_json).sort('_id', -1).skip(limit * (int(page_number) - 1)).limit(limit)

        total = customers_collection.count_documents(find_json)

        data_list =  list(data)
        json_data = dumps(data_list, indent = 2)  
        if not data_list:
            return Response({"error":"no records found"}, status= status.HTTP_404_NOT_FOUND)
        else: 
            response = {
                "count" :total,
                "total_pages": math.ceil(total/limit),
                "customers": json.loads(json_data)
            }
            return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
    
    if request.method == 'POST':
        try:
            request_body :dict = json.loads(request.body)

            existing = customers_collection.find({'customer_id': request_body['customer_id']})

            if not list(existing):
                customers_collection.insert_one(request_body)
            else:
                request_body.pop('_id')
                customers_collection.replace_one(filter={'customer_id': request_body['customer_id']}, replacement=request_body)
        


            return Response({"message": "Customer details updated"}, status=status.HTTP_200_OK)
        except Exception as e :
            print(e)

@api_view(['GET', 'POST'])
def get_stores(request :HttpRequest):

    if request.method == 'GET':
        page_number = request.GET['page_number']
        limit = int(request.GET['limit'])
        search_value = request.GET['search_value']


        find_json = {"$or" : [{'store_id': {"$regex" : search_value}}, {'store_name': {"$regex" : search_value}}, 
                            {'manager_contact': {"$regex" : search_value}}, 
                            {'manager_email': {"$regex" : search_value}}] }

        print(search_value)
        data = stores_collection.find(find_json).sort('_id', -1).skip(limit * (int(page_number) - 1)).limit(limit)

        total = stores_collection.count_documents(find_json)

        data_list =  list(data)
        json_data = dumps(data_list, indent = 2)  
        if not data_list:
            return Response({"error":"no records found"}, status= status.HTTP_404_NOT_FOUND)
        else: 
            response = {
                "count" :total,
                "total_pages": math.ceil(total/limit),
                "customers": json.loads(json_data)
            }
            return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
    
    if request.method == 'POST':
        try:
            request_body :dict = json.loads(request.body)

            existing = stores_collection.find({'store_name': request_body['store_name']})

            if not list(existing):
                stores_collection.insert_one(request_body)
            else:
                request_body.pop('_id')
                stores_collection.replace_one(filter={'store_name': request_body['store_name']}, replacement=request_body)
        


            return Response({"message": "Store details updated"}, status=status.HTTP_200_OK)
        except Exception as e :
            print(e)


@api_view(['GET', 'POST'])
def get_feedbacks(request :HttpRequest):

    if request.method == 'GET':
        page_number = request.GET['page_number']
        limit = int(request.GET['limit'])
        search_value = request.GET['search_value']
        store_id = request.GET['store_name']
        rating_from :str = request.GET['rating_from'].replace('+', " ")
        rating_to = request.GET['rating_to'].replace('+', " ")
        date_from = request.GET['date_from']
        date_to = request.GET['date_to']
        
        try:


            find_json = {"rating": {"$gte": int(rating_from), "$lte": int(rating_to)}}

            if search_value != "":
                find_json["invoice_fk"] = {"$regex" : search_value}

            if store_id != "":
                find_json["store_name"] = store_id

            if date_from != "":
                
                date_from = datetime.strptime(date_from, '%m-%d-%Y %H:%M:%S')
                date_to = datetime.strptime(date_to, '%m-%d-%Y %H:%M:%S')
                find_json["date"] = {"$gte": date_from, "$lte": date_to}

            print(find_json)
            if limit == 0:
                data = feedback_collection.find(find_json).sort('date', -1)
            else :
                data = feedback_collection.find(find_json).sort('date', -1).skip(limit * (int(page_number) - 1)).limit(limit)



            total = feedback_collection.count_documents(find_json)

            data_list =  list(data)
            json_data = dumps(data_list, indent = 2)  
            if not data_list:
                return Response({"error":"no records found"}, status= status.HTTP_404_NOT_FOUND)
            else: 
                limit = 1 if limit ==0 else  limit
                response = {
                    "count" :total,
                    "total_pages": math.ceil(total/limit ),
                    "feedback": json.loads(json_data)
                }
                return JsonResponse(response, status=status.HTTP_200_OK, safe=False)
        
        except Exception as e:
            print(e)
    else:
        request_body = json.loads(request.body)

        existing = feedback_collection.find({'invoice_fk': request_body['invoice_fk']})

        if not list(existing):
            feedback_collection.insert_one(request_body)
        else:
            feedback_collection.replace_one(filter={'invoice_fk': request_body['invoice_fk']}, replacement=request_body)
        
        return Response({"message": "Feedback added to the invoice"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def send_mail(request :HttpRequest):

    print(request.data['pdf'])
    try:
            with get_connection(  
            host=settings.EMAIL_HOST, 
        port=settings.EMAIL_PORT,  
        username=settings.EMAIL_HOST_USER, 
        password=settings.EMAIL_HOST_PASSWORD, 
        use_tls=settings.EMAIL_USE_TLS  
        ) as connection:  
                subject = 'Test Mail'
                email_from = settings.EMAIL_HOST_USER  
                recipient_list = ['pramodhdaniel5@gmail.com', request.data['mail'] ]  
                message = 'Test Mail'
                email = EmailMessage(subject, message, email_from, recipient_list, connection=connection)
                email.attach(f'invoice {random.randrange(20, 50, 3)}.pdf '
                             ,request.data['pdf'].read(), 'application/pdf')
                email.send()
    except Exception as e:
        print(e)

    return Response({"message": "Mail Sent"}, status=status.HTTP_200_OK)