from django.urls import path, include
from rest_framework.routers import DefaultRouter
from StockReport.views import *

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'product-records', ProductsOpeningStockViewSet)
# router.register(r'products-get', ProductOpeningStockViewSet)
# router.register(r'product-stock-records', ProductStockRecordViewSet)
router.register(r'stock-records', StockRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs
    path('product-stock-records/',ProductStockRecordViewSet.as_view()),
    path('stock-records/update/<int:id>/', StockRecordUpdateView.as_view(), name='stock-record-update'),
]
