from django.contrib import admin

from .models import ProcessStore


@admin.register(ProcessStore)
class ProcessStoreAdmin(admin.ModelAdmin):
    list_display = ['id', 'batch', 'quantity', 'expDate', 'created', 'updated','currentQuantity']
    search_fields = ['batch__batchName', 'quantity']
    list_filter = ['expDate', 'created', 'updated']
