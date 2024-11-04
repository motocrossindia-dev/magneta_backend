from django.urls import path

from sales.view.Products import products
# from sales.view.SalesData import orders
from sales.view.SalesLogin import login_distributor
from sales.view.CreateSalesPerson import sales_register
from sales.view.GetSalesPersons import get_sales_by_distributor, getCashInHand, transferCashInHand
from sales.view.collectDistributeMoney import collectMoney, getTransactions, distributeCollectedMoneyToOrders, \
    getSalesTransactions, getListOfTransactionsFromSalesToDistributor, SalesRetailerTransactionDetailView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sales.view.productdiscountView import ProductDiscountViewSet, ProductDiscountView

app_name = 'sales'



router = DefaultRouter()
router.register(r'discount', ProductDiscountViewSet)  # Register the viewset

urlpatterns = [
    path('', include(router.urls)),  # Include the router-generated URLs
    path('product_discounts/', ProductDiscountView.as_view(), name='product_discounts'),
    path('login_distributor/', login_distributor, name='login_user'),
    path('create_sales_person/', sales_register, name='create_sales_person'),
    path('get_sales_persons/', get_sales_by_distributor, name='get_sales_by_distributor'),
    # path('get_orders/', orders, name='orders'),
    path('get_products/', products, name='get_products'),

    path('collect_money/', collectMoney, name='collectMoney'),
    path('add_money_to_order/', distributeCollectedMoneyToOrders, name='distributeCollectedMoneyToOrders'),
    # path('get_transactions/', getTransactions, name='getTransactions'),
    path('get_payment_receipts/', getSalesTransactions, name='getSalesTransactions'),


    path('get_cash_in_hand/', getCashInHand, name='getCashInHand'),
    path('transfer_cash_in_hand/', transferCashInHand, name='transferCashInHand'),
    path('get_transfer_transactions/', getListOfTransactionsFromSalesToDistributor, name='getListOfTransactionsFromSalesToDistributor'),

    path('sales_retailer_transactions/<int:pk>/', SalesRetailerTransactionDetailView.as_view(), name='sales-retailer-transaction-detail'),
]

