from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from advertisements.models import Banner


# Register your models here.

# class Banner(models.Model):
#     image = models.ImageField(upload_to='images/')
#     title = models.CharField(max_length=100)
#     text = models.TextField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         verbose_name_plural = 'Banner'


@admin.register(Banner)
class BannerAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['id', 'title']

