from django.contrib import admin

import StockReport
from StockReport.models import *

# Register your models here.
@admin.register(OpeningStock)
class OpeningStockAdmin(admin.ModelAdmin):
    list_display = ['product','opening_stock','closing_stock','physical_stock']

@admin.register(ProductStockRecord)
class ProductStockReportAdmin(admin.ModelAdmin):
    list_display = ['product','opening_stock_units','production_units','sales_units','closing_stock_units','physical_stock',]
admin.site.register(StockRecord)
