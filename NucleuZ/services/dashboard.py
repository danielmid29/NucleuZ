from django.http import JsonResponse
from django.http import HttpRequest
from ..models import invoice_collection
from ..models import survey_and_marketing_collection
from ..models import company_info_collection
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

    message_success_count = message_collection.count_documents(filter={"$or":[{"status":"SUCCESS"}, {"status":"DELIVERED"}]})
    message_failed_count = message_collection.count_documents(filter={"$or":[{"status":"FAILED"}]})
    
    enabled_api = api_collection.count_documents(filter={"status": "enabled"})

    feedbacks = feedback_collection.count_documents(filter={})

    past_7_date = datetime.now() - dt.timedelta(days=7)
    
    message_success_graph_data = message_collection.find({"$or":[{"status":"SUCCESS"}, {"status":"DELIVERED"}, {"status":"QUEUED"}], "delivery_time":{"$gte":past_7_date}})
    message_failed_graph_data = message_collection.find({"$or":[{"status":"FAILED"}], "delivery_time":{"$gte":past_7_date}})

    response = {
        "invoice": invoice_count,
        "message_success":message_success_count,
        "message_failed":message_failed_count,
        "enabled_api": enabled_api,
        "feedbacks":feedbacks,
        "message_success_graph": get_graph_data(message_success_graph_data),
        "message_failed_graph":get_graph_data(message_failed_graph_data),
    }
    return Response(response, status=status.HTTP_200_OK)


def get_graph_data(data):
    message_success_graph :dict = {}
    count = 0 
    comp_date = ""
    for message in list(data):
        date = message['delivery_time']
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