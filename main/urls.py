from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from main import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls'), name='accounts'),
    path('sales/', include('sales.urls'), name='sales'),
    path('advertisements/', include('advertisements.urls'), name='advertisements'),
    path('inventory/', include('inventory.urls'), name='inventory'),
    path('process_store/', include('process_store.urls'), name='process_store'),
    path('process_batch/', include('process_batch.urls'), name='process_batch'),
    path('products/', include('products.urls'), name='products'),
    path('orders/', include('orders.urls'), name='orders'),
    path('retailers/', include('retailers.urls'), name='retailers'),
    path('app/', include('update_app.urls'), name='update_app'),
    path('distributors/', include('distributors.urls'), name='distributors'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('report/', include('StockReport.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
