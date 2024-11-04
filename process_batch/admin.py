from django.contrib import admin

from process_batch.models.batchMixChocolateIceCreamTemplate import *
from process_batch.models.batchMixkulfyTemplate import BatchMixkulfyTemplate, BatchMixkulfyTemplateIngredients
from process_batch.models.categories import *
from process_batch.models.BatchMix import *
from process_batch.models.BatchMixIceCream import *
from process_batch.models.batchMixTemplate import *
@admin.register(BatchMixIngredients)
class BatchmixIngredients(admin.ModelAdmin):
    list_display = ('id','SyrupBatchMix','SyrupBatchMix_id' ,'grnlist',)
    # pass

@admin.register(BatchMix)
class BatchmixAdmin(admin.ModelAdmin):
    list_display = ['id','batchName','expDate','is_expired']
    # pass
@admin.register(BatchMixTemplateIngredients)
class BatchmixTemplateIngredients(admin.ModelAdmin):
    # list_display = ['id']
    pass

admin.site.register(BatchMixSubCategory)
admin.site.register(BatchMixCategory)

admin.site.register(BatchMixIceCreamTemplate)
admin.site.register(BatchMixIceCreamTemplateIngredients)
admin.site.register(BatchMixTemplate)
# admin.site.register(BatchMixTemplateIngredients)
admin.site.register(BatchMixChocolateIceCreamTemplate)
admin.site.register(BatchMixChocolateIceCreamTemplateIngredients)
admin.site.register(BatchMixkulfyTemplate)
admin.site.register(BatchMixkulfyTemplateIngredients)

# ===================================

