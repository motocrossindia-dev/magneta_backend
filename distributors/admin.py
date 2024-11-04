from django.contrib import admin

from distributors.models import RetailerMainOrders
from distributors.models import RetailerOrders
# from inventory.models import SyrupBatchMixIngredientGRN
from .models import DistributorStock


# Register your models here.

class RetailerMainOrdersAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order_number', 'distributor', 'order_date', 'mode_of_payment', 'payment_status', 'CGST', 'SGST',
        'IGST', 'gst_rate', 'sub_total', 'grand_total', 'pending_amount')
    list_filter = ('order_date', 'distributor',)
    ordering = ('-id',)


class RetailerOrdersAdmin(admin.ModelAdmin):
    list_display = ['id', 'retailer_main_order', 'product_id', 'product_name', 'quantity', 'carton_size',
                    'price_per_carton', 'sum', 'CGST', 'SGST', 'IGST', 'gst', 'amount']
    list_filter = ('retailer_main_order',)
    ordering = ['-id']


class DistributorStockAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'distributor_id', 'quantity', 'created', 'updated')
    list_filter = ('product_id', 'distributor_id')
    search_fields = ('product_id__name', 'distributor_id__username')
    ordering = ('-created',)


admin.site.register(RetailerMainOrders, RetailerMainOrdersAdmin)
admin.site.register(RetailerOrders, RetailerOrdersAdmin)
admin.site.register(DistributorStock, DistributorStockAdmin)
# admin.site.register(SyrupBatchMixIngredientGRN)
