from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Vendor, VendorContactPersons, SecurityNote, Store, SubType, StoreHistory, \
    StoreGRN
from django.contrib import admin
from .models import Material, Type, GoodsReturnNote


@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('vendorFullname', 'enterpriseName', 'vendorAddress', 'vendorGSTno')
    search_fields = ('vendorFullname', 'enterpriseName', 'vendorGSTno')


@admin.register(VendorContactPersons)
class VendorContactPersonsAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('VCPname', 'phoneNumber', 'vendor')
    search_fields = ('VCPname', 'phoneNumber', 'vendor__enterpriseName')


@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('materialName', 'materialDescription','id')
    search_fields = ('materialName', 'materialDescription')


@admin.register(Type)
class TypeAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('typeName',)
    search_fields = ('typeName',)


@admin.register(SubType)
class TypeAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('subTypeName',)
    search_fields = ('subTypeName',)


@admin.register(GoodsReturnNote)
class GoodsReturnNoteAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id','is_expired', 'GRNnumber', 'materialName', 'typeName', 'vendor', 'mfgDate', 'billNo',
                    'receivedBy', 'receivedDate', 'measure', 'unitSize', 'quantityPerPackage',
                    'unitPrice', 'damage', 'description', 'created', 'updated')
    list_filter = ('materialName', 'typeName', 'vendor', 'mfgDate', 'receivedDate','unitSize')
    search_fields = ('GRNnumber', 'billNo', 'description')


# @admin.register(SyrupBatchMix)
# class SyrupBatchMixAdmin(admin.ModelAdmin):
#     list_display = ('id', 'batchName', 'batchCode', 'batchDate', 'subCategory', 'totalVolume', 'created')
#     list_filter = ('batchName', 'batchCode', 'batchDate', 'subCategory', 'totalVolume')
#     search_fields = ('batchName', 'batchCode', 'batchDate', 'subCategory', 'totalVolume', 'created')


# @admin.register(BatchMixTemplate)
# class BatchMixTemplateAdmin(admin.ModelAdmin):
#     list_display = ('id', 'batchName', 'batchCode', 'subCategory', 'expDays')


admin.site.register(SecurityNote)
admin.site.register(Store)
admin.site.register(StoreHistory)
admin.site.register(StoreGRN)
# admin.site.register(Batch)
# admin.site.register(BatchIngredients)
# admin.site.register(BatchMixCategory)
# admin.site.register(BatchMixSubCategory)

# admin.site.register(BatchMixTemplate)
# admin.site.register(BatchMixTemplateIngredients)

# admin.site.register(SyrupBatchMix)
# admin.site.register(SyrupBatchMixIngredients)
