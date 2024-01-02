"""
URL configuration for NucleuZ project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path
from .services import invoice_api
from .services import send_invoice
from .services import table_details
from .services import dashboard
from .services import template
from .services import invoice_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('invoice-api/', invoice_api.get_invoice_details),
    path('invoice-check', invoice_api.check_new_invoice),
    path('invoices-api/add/', invoice_api.invoice_api),
    path('invoices-api/test/', invoice_api.test_api),
    path('send', send_invoice.send_invoice),
    path('send/', send_invoice.send_invoice),
    re_path('invoices', table_details.get_invoices),
    path('invoice', template.get_template_with_details),
    path('message', table_details.get_messages),
    path('stores', table_details.get_stores),
    path('customers', table_details.get_customers),
    path('feedback', table_details.get_feedbacks),
    path('rating', dashboard.get_rating),
    path('dashboard', dashboard.get_dashboard),
    path('template', template.save_template),
]

invoice_api.runScheduler()