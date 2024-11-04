from django.contrib import admin

from .models import AppVersionNumber, PartnerAppVersionNumber, IphoneAppVersionNumber, IphonePartnerAppVersionNumber

admin.site.register(AppVersionNumber)
admin.site.register(PartnerAppVersionNumber)
admin.site.register(IphoneAppVersionNumber)
admin.site.register(IphonePartnerAppVersionNumber)