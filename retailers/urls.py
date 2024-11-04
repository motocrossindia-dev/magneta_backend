from django.urls import path

from retailers.view.CustomerMainOrders import customer_main_order
from retailers.view.CustomerOrders import customer_orders

app_name = 'retailers'

urlpatterns = [
    path('customer_orders/', customer_orders, name='customer_orders'),
    path('customer_orders/<int:pk>/', customer_orders, name='customer_orders'),

    path('customer_main_orders/', customer_main_order, name='customer_main_order')
]
