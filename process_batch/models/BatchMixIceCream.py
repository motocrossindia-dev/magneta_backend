from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from process_batch.models.categories import BatchMixSubCategory


class BatchMixIceCreamTemplate(models.Model):
    batchName = models.CharField(max_length=100)
    batchCode = models.CharField(max_length=100)
    expDays = models.CharField(max_length=10)
    subCategory = models.ForeignKey(BatchMixSubCategory, on_delete=models.CASCADE,related_name='batchMixIceCreamSubCategory')

    # ======================
    milk_fat_percentage=models.FloatField(default=0.0)
    milk_snf_percentage=models.FloatField()
    batch_fat_percentage=models.FloatField()
    batch_snf_percentage=models.FloatField()
    cream_percentage=models.FloatField()
    butter_percentage=models.FloatField()
    smp_snf_percentage=models.FloatField()
    standard_converstion_factor=models.FloatField()

    is_deleted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.batchName)

    class Meta:
        verbose_name_plural = "BatchMixIceCreamTemplate"


class BatchMixIceCreamTemplateIngredients(models.Model):
    type_choice = (("RMStore", "RMStore"), ("ProcessStore", "ProcessStore"))
    template = models.ForeignKey(BatchMixIceCreamTemplate, on_delete=models.CASCADE, related_name="ingredients")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=type_choice, default="RMStore")

    # ingredient = models.ForeignKey(Material, on_delete=models.CASCADE,null=True, blank=True)
    ingredient = GenericForeignKey('content_type', 'object_id')
    lowerLimit = models.FloatField(max_length=20)
    percentage = models.FloatField(max_length=20)
    upperLimit = models.FloatField(max_length=20)
    # rate = models.FloatField(max_length=20)

    is_deleted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.template.batchName}"

    class Meta:
        verbose_name_plural = "BatchMixIceCreamTemplateIngredients"
