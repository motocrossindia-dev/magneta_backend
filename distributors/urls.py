from django.urls import path

from distributors.view.InvoiceTemp import invoice_temp
from distributors.view.LetterPDF import letter_pdf_temp
from distributors.view.RetailerMainOrders import retailer_main_orders, get_sales_person_orders
from distributors.view.RetailerOrders import retailer_orders, distributor_today_collection
from distributors.view.Retailers import retailers
from distributors.view.TaxInvoice import tax_invoice, generate_receipt_pdf, DistributorStatsAPIView
from distributors.view.search_retailer_orders import search_retailer_orders
from distributors.views import  calculate_invoice_api

# from distributors.view.temp import tax_invoice

app_name = 'distributors'

urlpatterns = [
    path('retailers/', retailers, name='retailers'),
    path('retailer_order/', retailer_main_orders, name='retailer_orders'),
    path('retailer_order/<int:pk>/', retailer_main_orders, name='retailer_orders'),
    path('orders_details/', retailer_orders, name='orders_details'),
    path('orders_details/<int:pk>/', retailer_orders, name='orders_details'),

    path('search_retailer_orders/', search_retailer_orders, name='search_retailer_orders'),

    path('tax_invoice/<int:pk>/', tax_invoice, name='tax_invoice'),
    path('todays_collection/', distributor_today_collection, name='distributor_today_collection'),

    path('invoice_temp/<int:pk>/', invoice_temp, name='invoice_temp'),
    path('letter_pdf/', letter_pdf_temp, name='letter_pdf'),

    path('get_sales_person_orders/<int:pk>/', get_sales_person_orders, name='get_sales_person_orders'),

    path('calculate_invoice/<int:order_id>/', calculate_invoice_api, name='calculate_invoice'),


    path('generate-receipt/<int:pk>/', generate_receipt_pdf, name='generate-receipt'),


    path('distributor_stats/', DistributorStatsAPIView.as_view(), name='distributor-stats')
]
