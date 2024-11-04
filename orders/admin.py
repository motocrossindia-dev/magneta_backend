from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from orders.models import MainOrders, Order, GST, PaymentTrack, FactoryToCustomer


# Register your models here.

# mode_of_payment = models.CharField(max_length=15, default="Cash")
#     payment_status = models.CharField(max_length=20, default="Unpaid")
#     CGST = models.FloatField(max_length=5, default=0.00)
#     SGST = models.FloatField(max_length=5, default=0.00)
#     IGST = models.FloatField(max_length=5, default=0.00)
#     grand_total = models.FloatField(max_length=10, default=0.00)

class MainOrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'distributor', 'order_date', 'mode_of_payment', 'status', 'payment_status', 'CGST', 'SGST',
                    'IGST', 'gst', 'sub_total', 'grand_total')
    list_filter = ('order_date', 'distributor',)
    ordering = ('-id',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'main_order', 'product_name', 'requested_quantity', 'accepted_quantity', 'factory_base_price',
                    'factory_gst_price', 'factory_sale', 'carton_size', 'price_per_carton', 'mrp', 'discount',
                    'discount_amount', 'sum', 'CGST', 'SGST', 'IGST', 'gst', 'amount')
    list_filter = ('main_order',)
    ordering = ('id',)


class PaymentTrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'main_order', 'status', 'utrNo', 'cash', 'cheque', 'credit', 'updated_by', 'updator_contact',
                    'created')
    list_filter = ('main_order',)
    ordering = ('id',)


class GSTAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'gst', 'cgst', 'sgst', 'igst')
    list_filter = ('gst',)
    ordering = ('id',)


class FactoryToCustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'sold_by', 'product_name', 'order_date', 'mode_of_payment', 'payment_status',
                    'quantity', 'mrp', 'amount']
    ordering = ('-id',)


admin.site.register(MainOrders, MainOrdersAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(PaymentTrack, PaymentTrackAdmin)

admin.site.register(GST, GSTAdmin)
admin.site.register(FactoryToCustomer, FactoryToCustomerAdmin)
