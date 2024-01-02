from django.http import JsonResponse
from django.http import HttpRequest
from ..models import invoice_collection
from ..models import survey_and_marketing_collection
from ..models import company_info_collection
from ..models import customers_collection
from ..models import stores_collection
from ..models import message_collection
from ..models import feedback_collection
from ..models import api_collection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from bson.json_util import dumps
import math
from datetime import datetime
import datetime as dt


@api_view(['GET'])
def get_dashboard(request):
    
    invoice_count = invoice_collection.count_documents(filter={})

    message_success_count = message_collection.count_documents(filter={"$or":[{"status":"SUCCESS"}, {"status":"DELIVERED"}, {"status":"QUEUED"}]})
    message_failed_count = message_collection.count_documents(filter={"$or":[{"status":"FAILED"}, {"status":"Failed"}]})
    
    enabled_api = api_collection.count_documents(filter={"status": "enabled"})

    feedbacks = feedback_collection.count_documents(filter={})
    customers_count = customers_collection.count_documents(filter={})

    past_7_date = datetime.now() - dt.timedelta(days=7)
    
    message_success_graph_data = message_collection.find({"$or":[{"status":"SUCCESS"}, {"status":"DELIVERED"}, {"status":"QUEUED"}], "date":{"$gte":past_7_date}})
    message_failed_graph_data = message_collection.find({"$or":[{"status":"FAILED"}, {"status":"Failed"}], "date":{"$gte":past_7_date}})
    
    feedback_graph_data = feedback_collection.find({}).sort('rating', 1)
    data_list =  list(feedback_graph_data)
    json_data = dumps(data_list, indent = 2) 

    invoice_graph_data = invoice_collection.find({}).sort('date', 1)
    invoice_data_list =  list(invoice_graph_data)
    invoice_json_data = dumps(invoice_data_list, indent = 2) 

    total_income = 0

    for invoice in json.loads(invoice_json_data):
        total_income = total_income + invoice['total']

    print(total_income)

    store_graph_data = stores_collection.find({})
    store_data_list =  list(store_graph_data)
    store_json_data = dumps(store_data_list, indent = 2) 

    store_name_list = []

    for store in json.loads(store_json_data):
        store_name_list.append(store['store_name'])


    print(store_name_list)
    
    response = {
        "total_income":total_income,
        "customers":customers_count,
        "invoice": invoice_count,
        "message_success":message_success_count,
        "message_failed":message_failed_count,
        "enabled_api": enabled_api,
        "feedbacks":feedbacks,
        "store_names":store_name_list,
        "message_failed_graph":get_graph_data(message_failed_graph_data),
        "message_success_graph": get_graph_data(message_success_graph_data),
        "rating_graph":get_rating_graph_data(json.loads(json_data)),
        "invoice_graph":get_invoice_graph_data(json.loads(invoice_json_data)),
    }
    print(response)
    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_rating(request):
    
    store_id = request.GET['store_name']
    rating_from = request.GET['rating_from']
    rating_to = request.GET['rating_to']
    date_from = request.GET['date_from']
    date_to = request.GET['date_to']
        
    try:


        find_json = {"rating": {"$gte": int(rating_from), "$lte": int(rating_to)}}


        if store_id != "":
            find_json["store_name"] = store_id

        if date_from != "":
                
            date_from = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
            date_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
            find_json["date"] = {"$gte": date_from, "$lte": date_to}

        print(find_json)
        
        data = feedback_collection.find(find_json).sort('date', 1)


        data_list =  list(data)
        json_data = dumps(data_list, indent = 2)  
    except Exception as e:
        print(e)
        
    if not data_list:
        return Response({"error":"no records found"}, status= status.HTTP_404_NOT_FOUND)
    else: 
        response = {"rating":get_rating_graph_data(json.loads(json_data))}
        return JsonResponse(response, status=status.HTTP_200_OK, safe=False)

def get_graph_data(data):
    message_success_graph :dict = {}
    count = 0 
    comp_date = ""
    for message in list(data):
        date = message['date']
        date_str = str(date)
        date_str =  date_str[0:10]

        if len(comp_date) ==0:
            comp_date = date_str

        if comp_date == date_str:
            message_success_graph[date_str] = count+1
            count = count+1
        else:
            count = 0
            comp_date = date_str
            message_success_graph[date_str] = count+1
            count = count+1


    message_success_graph_list = []
    keys= message_success_graph.keys()

    for key in keys:
        message_success_graph_list.append({
            "date": key,
            "count": message_success_graph[key]
        })
    
    return message_success_graph_list

def get_invoice_graph_data(data):
    invoice_graph :dict = {}
    balance = 0 
    comp_date = ""
    try:
        for invoice in list(data):
            date = invoice['date']
            date_str = str(date)
            

            if len(comp_date) ==0:
                comp_date = date_str

            if comp_date == date_str:
                invoice_graph[date_str] = balance+int(invoice['total'])
                balance = balance+int(invoice['total'])
            else:
                balance = 0
                comp_date = date_str
                invoice_graph[date_str] = balance+int(invoice['total'])
                balance = balance+int(invoice['total'])


    except Exception as e:
        print(e)

    invoice_list = []
    keys= invoice_graph.keys()

    for key in keys:
        invoice_list.append({
            "date": key,
            "balance": invoice_graph[key]
        })
    return invoice_list

def get_rating_graph_data(data):
    rating_graph :dict = {}
    try:
        count = 0 
        comp_rate = ""
        for rating in list(data):
            rating_str = str(rating['rating'])
            print(comp_rate)
            if len(comp_rate) ==0:
                comp_rate = rating_str

            if comp_rate == rating_str:
                rating_graph[rating_str] = count+1
                count = count+1
            else:
                count = 0
                comp_rate = rating_str
                rating_graph[rating_str] = count+1
                count = count+1
        

        rating_list = []
        keys= rating_graph.keys()
    except Exception as e :
        print(e)
    for key in keys:
        rating_list.append({
            "rating": key,
            "count": rating_graph[key]
        })
    
    return rating_list