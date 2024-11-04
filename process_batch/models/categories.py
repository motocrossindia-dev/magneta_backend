from django.db import models


# --------------------------------------------------------------------------------------------------------------------
#                                                 Batch Mix Categories Models
# --------------------------------------------------------------------------------------------------------------------
class BatchMixCategory(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    # class Meta:
    #     verbose_name_plural = "BatchMixCategory"
    #

class BatchMixSubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(BatchMixCategory, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    #
    # class Meta:
    #     verbose_name_plural = "BatchMixSubCategory"

