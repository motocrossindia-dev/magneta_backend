from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from accounts.models import UserBase, Otp, UserTargetAmount
from .models import CompanyInformation, Role, RolesPermission

class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'is_manager', 'is_distributor', 'is_retailer', 'is_store_manager',
                    'phone_number', 'is_active', 'is_staff', 'enterprise_name')
    list_filter = ('phone_number', 'email', 'phone_number',)
    ordering = ('id',)

class OtpAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'otp', 'user',)
    list_filter = ('otp', 'user',)
    ordering = ('id',)


class RoleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
class RolesPermissionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
class CompanyInformationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'legal_name', 'brand_name', 'pan', 'gstin', 'created', 'updated')
    search_fields = ('legal_name', 'brand_name', 'pan', 'gstin')
    list_filter = ('created', 'updated')
    readonly_fields = ('created', 'updated')

admin.site.register(UserBase, UserAdmin)
admin.site.register(Otp, OtpAdmin)
admin.site.register(CompanyInformation, CompanyInformationAdmin)

admin.site.register(Role,RoleAdmin)
admin.site.register(RolesPermission,RolesPermissionAdmin)
admin.site.register(UserTargetAmount)

# from django.contrib import admin
# from accounts.models import UserBase, Otp
# from .models import CompanyInformation,Role,RolesPermission
#
#
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'email', 'first_name', 'is_manager', 'is_distributor', 'is_retailer', 'is_store_manager',
#                     'phone_number', 'is_active', 'is_staff', 'enterprise_name')
#     list_filter = ('phone_number', 'email', 'phone_number',)
#     ordering = ('id',)
#
#
# class OtpAdmin(admin.ModelAdmin):
#     list_display = ('id', 'otp', 'user',)
#     list_filter = ('otp', 'user',)
#     ordering = ('id',)
#
#
# class CompanyInformationAdmin(admin.ModelAdmin):
#     list_display = ('id', 'legal_name', 'brand_name', 'pan', 'gstin', 'created', 'updated')
#     search_fields = ('legal_name', 'brand_name', 'pan', 'gstin')
#     list_filter = ('created', 'updated')
#     readonly_fields = ('created', 'updated')
#
#
# admin.site.register(UserBase, UserAdmin)
# admin.site.register(Otp, OtpAdmin)
# admin.site.register(CompanyInformation, CompanyInformationAdmin)
#
# admin.site.register(Role)
# admin.site.register(RolesPermission)
