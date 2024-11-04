from django.urls import path, re_path

from orders.view.Dashboard import dashboard
from orders.view.FactoryDirectSale import factory_direct_sale
from orders.view.FactoryToCustomer import factory_to_customer
from orders.view.GST import gst
from orders.view.Get_pdf import tax_invoice
from orders.view.MainOrders import main_orders, search_main_orders
from orders.view.Orders import orders, distributor_orders
from orders.view.Stock import stock

from orders.view.Varifying_Payment import verifying_payment

app_name = 'orders'

urlpatterns = [
    re_path(r'^main_orders/(?P<pk>\d+)?$', main_orders, name='main_orders'),
    re_path(r'^orders_details/(?P<pk>\d+)?$', orders, name='orders'),
    re_path(r'^distributor_orders/(?P<pk>\d+)?$', distributor_orders, name='distributor_orders'),
    re_path(r'^gst/(?P<pk>\d+)?$', gst, name='gst'),
    re_path(r'^verifying_payment/(?P<pk>\d+)/$', verifying_payment, name='verifying_payment'),

    path('bill_pdf/<int:pk>/', tax_invoice, name='tax_invoice'),
    path('dashboard/', dashboard, name='dashboard'),
    path('factory_to_customer/', factory_to_customer, name='factory_to_customer'),
    path('search_main_orders/', search_main_orders, name='search_main_orders'),
    path('user_stock/<int:pk>/', stock, name='stock'),
    path('factory_direct_sale/', factory_direct_sale, name='factory_direct_sale'),
]
