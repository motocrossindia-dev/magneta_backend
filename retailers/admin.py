from django.contrib import admin
from .models import CustomerMainOrders, CustomerOrders


class CustomerMainOrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'retailer', 'orderDate', 'customerFullName', 'customerPhoneNumber', 'grandTotal')
    list_filter = ('retailer', 'orderDate')
    search_fields = ('customerFullName', 'customerPhoneNumber', 'orderNumber')


class CustomerOrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'customerMainOrder', 'productId', 'productName', 'quantity', 'mrp', 'sum')
    list_filter = ('customerMainOrder', 'productId')
    search_fields = ('productId', 'productName')


admin.site.register(CustomerMainOrders, CustomerMainOrdersAdmin)
admin.site.register(CustomerOrders, CustomerOrdersAdmin)
