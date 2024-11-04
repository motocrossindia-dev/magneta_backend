from datetime import date

from django.db import models
from django.utils import timezone

from accounts.models import UserBase


class Vendor(models.Model):
    vendorFullname = models.CharField(max_length=50)
    enterpriseName = models.CharField(max_length=50)
    vendorAddress = models.CharField(max_length=50)
    vendorGSTno = models.CharField(max_length=50)

    class Meta:
        unique_together = ('enterpriseName', 'vendorGSTno')

    def __str__(self):
        return str(self.enterpriseName)


class VendorContactPersons(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT,related_name='contactPersons')
    VCPname = models.CharField(max_length=50)
    phoneNumber = models.CharField(max_length=10)

    def __str__(self):
        return str(self.vendor) + ' - ' + str(self.VCPname)


class Type(models.Model):
    typeName = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return str(self.typeName)


class SubType(models.Model):
    subTypeName = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return str(self.subTypeName)


class Material(models.Model):
    materialName = models.CharField(max_length=50)
    materialDescription = models.CharField(max_length=50)
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    subType = models.ForeignKey(SubType, blank=True, null=True, on_delete=models.PROTECT,related_name='materials_subtype')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.materialName)

    class Meta:
        unique_together = ('materialName', 'type')


class SecurityNote(models.Model):
    # GRNnumber = models.CharField(max_length=20,blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    vehicleNo = models.CharField(max_length=20)
    billNo = models.CharField(max_length=20)
    invoiceImage = models.ImageField(upload_to="media/static/invoiceImage/", blank=True, null=True)

    is_converted_to_grn = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"{self.billNo}-{self.vendor}")


class GoodsReturnNote(models.Model):
    unit_choices = (
        ('Ml', 'Ml'),
        ('Gm', 'Gm'),
        ('Kg', 'Kg'),
        ('Litre', 'Litre'),
        ('Tonnes', 'Tonnes'),
    )
    GRNnumber = models.CharField(max_length=20)
    materialName = models.ForeignKey(Material, on_delete=models.PROTECT)
    typeName = models.ForeignKey(Type, on_delete=models.PROTECT)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT,related_name="goods_return_vendor")
    mfgDate = models.DateField()
    expDate = models.DateField()
    billNo = models.CharField(max_length=40)
    receivedBy = models.ForeignKey(UserBase, on_delete=models.PROTECT, null=True, blank=True)
    receivedDate = models.DateField(null=True, blank=True)
    batchNumber = models.CharField(max_length=100, null=True, blank=True)
    grnMaterialDescription = models.CharField(max_length=100, null=True, blank=True)

    measure = models.CharField(max_length=10, choices=unit_choices, default="Kg")
    unitSize = models.FloatField(max_length=10, null=True, blank=True)
    quantityPerPackage = models.IntegerField(null=True, blank=True)
    unitPrice = models.FloatField(max_length=10, null=True, blank=True)

    packageType = models.CharField(max_length=50, null=True, blank=True)
    otherPackageType = models.CharField(max_length=100, null=True, blank=True)
    totalQuantity = models.FloatField(max_length=10, null=True, blank=True)
    totalPrice = models.FloatField(max_length=10, null=True, blank=True)
    approvedQuantity = models.FloatField(max_length=10, null=True, blank=True)
    approvedPrice = models.FloatField(max_length=10, null=True, blank=True)

    # damage details
    damage = models.IntegerField(null=True, blank=True)
    damageSubject = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # rejection details
    rejectedCompletely = models.BooleanField(default=False)
    rejectedQuantity = models.FloatField(max_length=10, null=True, blank=True)
    rejectedReason = models.TextField(null=True, blank=True)

    rejectedImage1 = models.ImageField(upload_to='grn/rejectionImages/', blank=True, null=True)
    rejectedImage2 = models.ImageField(upload_to='grn/rejectionImages/', blank=True, null=True)
    rejectedImage3 = models.ImageField(upload_to='grn/rejectionImages/', blank=True, null=True)

    qualityCheckBy = models.ForeignKey(UserBase, on_delete=models.PROTECT, null=True, blank=True,related_name='quality_check_by')
    QCDateTime = models.DateTimeField(null=True, blank=True)

    vehicleNumber = models.CharField(max_length=20, null=True, blank=True)

    damageImage1 = models.ImageField(upload_to='grn/', blank=True, null=True)
    damageImage2 = models.ImageField(upload_to='grn/', blank=True, null=True)
    damageImage3 = models.ImageField(upload_to='grn/', blank=True, null=True)

    invoiceImage = models.ImageField(upload_to='grn/', blank=True, null=True)
    securityNote = models.ForeignKey(SecurityNote, on_delete=models.PROTECT, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_expired = models.BooleanField(default=False)
    def __str__(self):
        return str(self.GRNnumber)

    class Meta:
        verbose_name = 'GoodsReceivedNote'

    def is_expired_check(self):
        return self.expDate < timezone.now().date()

# ====================================================================================================================
#                                                      Store
# ====================================================================================================================
class Store(models.Model):
    unit_choices = (
        ('Ml', 'Ml'),
        ('Gm', 'Gm'),
        ('Kg', 'Kg'),
        ('Litre', 'Litre'),
    )

    materialName = models.OneToOneField(Material, on_delete=models.PROTECT)
    typeName = models.ForeignKey(Type, on_delete=models.PROTECT,null=True, blank=True)
    measure = models.CharField(max_length=10, choices=unit_choices, default="Kg")
    totalQuantity = models.FloatField()
    currentQuantity = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.materialName)

    class Meta:
        verbose_name = 'Store'
        unique_together = ('materialName', 'typeName')


class StoreHistory(models.Model):
    materialName = models.ForeignKey(Material, on_delete=models.PROTECT)
    CurrentQuantity = models.FloatField()
    ConsumedQuantity = models.FloatField()
    RemainingQuantity = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.materialName)


class StoreGRN(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    grn = models.ForeignKey(GoodsReturnNote, on_delete=models.CASCADE)
    quantity = models.FloatField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store.materialName.materialName}-{self.grn.GRNnumber}"



# --------------------------------------------------------------------------------------------------------------------
#                                                 End Of Store
# --------------------------------------------------------------------------------------------------------------------

# ====================================================================================================================
#                                                      BATCH
# ====================================================================================================================
# Batch Generation and creating different batches

# class Batch(models.Model):
#     batchName = models.CharField(max_length=100)
#     batchCode = models.CharField(max_length=100)
#     # batchIngredients = models.ManyToManyField(BatchIngredients)
#     totalAmount = models.FloatField(max_length=20)
#     totalQuantity = models.FloatField(max_length=20)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def save(self, *args, **kwargs):
#         if self.totalQuantity is not None:
#             self.totalQuantity = round(self.totalQuantity, 3)
#         super(Batch, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return str(self.batchName)
#
#     class Meta:
#         verbose_name_plural = "Batch"


# class BatchIngredients(models.Model):
#     materialName = models.ForeignKey(Material, on_delete=models.PROTECT)
#     quantity = models.FloatField(max_length=20)
#     price = models.FloatField(max_length=20)
#     total = models.FloatField(max_length=20)
#     batch = models.ForeignKey(Batch, on_delete=models.PROTECT)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def save(self, *args, **kwargs):
#         if self.quantity is not None:
#             self.quantity = round(self.quantity, 3)
#         super(BatchIngredients, self).save(*args, **kwargs)
#
#     class Meta:
#         verbose_name_plural = "BatchIngredients"


# --------------------------------------------------------------------------------------------------------------------
#                                                 End Of Batch
# --------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------
#                                                 Batch Mix Categories Models
# --------------------------------------------------------------------------------------------------------------------
# class BatchMixCategory(models.Model):
#     name = models.CharField(max_length=100)
#     is_deleted = models.BooleanField(default=False)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return str(self.name)
#
#     class Meta:
#         verbose_name_plural = "BatchMixCategory"


# class BatchMixSubCategory(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(BatchMixCategory, on_delete=models.CASCADE)
#     is_deleted = models.BooleanField(default=False)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return str(self.name)
#
#     class Meta:
#         verbose_name_plural = "BatchMixSubCategory"


# --------------------------------------------------------------------------------------------------------------------
#                                                 Batch Mix Template
# --------------------------------------------------------------------------------------------------------------------

# class BatchMixTemplate(models.Model):
#     batchName = models.CharField(max_length=100)
#     batchCode = models.CharField(max_length=100)
#     expDays = models.CharField(max_length=10)
#     subCategory = models.ForeignKey(BatchMixSubCategory, on_delete=models.CASCADE)
#
#     is_deleted = models.BooleanField(default=False)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return str(self.batchName)
#
#     class Meta:
#         verbose_name_plural = "BatchMixTemplate"
#
#
# class BatchMixTemplateIngredients(models.Model):
#     type_choice = (("RMStore", "RMStore"), ("ProcessStore", "ProcessStore"))
#     template = models.ForeignKey(BatchMixTemplate, on_delete=models.CASCADE, related_name="ingredients")
#     ingredient = models.ForeignKey(Material, on_delete=models.CASCADE,null=True, blank=True)
#     type = models.CharField(max_length=20,choices=type_choice,default="RMStore")
#     process_store = models.ForeignKey('process_store.ProcessStoreSyrupAndSauce', on_delete=models.CASCADE, null=True, blank=True,related_name="process_store_ingredients")
#     lowerLimit = models.FloatField(max_length=20)
#     percentage = models.FloatField(max_length=20)
#     upperLimit = models.FloatField(max_length=20)
#     # rate = models.FloatField(max_length=20)
#
#     is_deleted = models.BooleanField(default=False)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.template.batchName}"
#
#     class Meta:
#         verbose_name_plural = "BatchMixTemplateIngredients"


# --------------------------------------------------------------------------------------------------------------------
#                                                 Syrup and sauce Batch Mix Models
# --------------------------------------------------------------------------------------------------------------------

# class SyrupBatchMix(models.Model):
#     batchName = models.CharField(max_length=100)
#     batchCode = models.CharField(max_length=100)
#     batchDate = models.DateField()
#     expDate = models.DateField(null=True, blank=True)
#     subCategory = models.ForeignKey(BatchMixSubCategory, on_delete=models.CASCADE)
#     totalVolume = models.FloatField(max_length=20)
#
#     is_deleted = models.BooleanField(default=False)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return str(self.batchName)
#
#     class Meta:
#         verbose_name_plural = "SyrupBatchMix"

#
# class SyrupBatchMixIngredients(models.Model):
#     # added post signal to signals.py
#     SyrupBatchMix = models.ForeignKey(SyrupBatchMix, on_delete=models.CASCADE)
#     ingredient = models.ForeignKey(Material, on_delete=models.CASCADE)
#     percentage = models.FloatField(max_length=20)
#     quantity = models.FloatField(max_length=20)
#     grnlist = models.JSONField(default=list)
#
#     rate = models.FloatField(max_length=20, default=0.0)
#
#     is_deleted = models.BooleanField(default=False)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return str(self.SyrupBatchMix.batchName)
#
#     class Meta:
#         verbose_name_plural = "SyrupBatchMixIngredients"

