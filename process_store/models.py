from datetime import date

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from process_batch.models.BatchMix import BatchMix


class ProcessStore(models.Model):
    batch = models.ForeignKey(BatchMix, on_delete=models.CASCADE)
    quantity = models.FloatField(max_length=20)
    expDate = models.DateField()
    currentQuantity = models.FloatField(max_length=20,default=0.0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.batch)

    def is_expired(self):
        """Check if the batch is expired."""
        print(self.batch.expDate < date.today(),'================data')
        return self.batch.expDate < date.today()

    def deduct_quantity(self, deduction_amount):
        """Deduct the quantity if the batch is not expired and has sufficient current quantity."""
        self.currentQuantity -= deduction_amount
        self.save()

        return self.currentQuantity
    # def deduct_quantity(self, deduction_amount):
    #     """Deduct the quantity if the batch is not expired."""
    #     if not self.is_expired():
    #         self.currentQuantity -= deduction_amount
    #         self.save()
    #     else:
    #         raise ValueError("Cannot deduct quantity from an expired batch.")

@receiver(post_save, sender=BatchMix)
def batch_post_save_receiver(sender, instance, created, *args, **kwargs):
    """
    after saved in the database
    """
    if created:
        try:
            process = ProcessStore.objects.get(batch__batchName__exact=instance.batchName,batch__subCategory__category=instance.subCategory.category)
            print(process,'---------------getting')
            process.quantity = process.quantity +instance.totalVolume
            process.currentQuantity =process.currentQuantity + instance.totalVolume
            process.save()
            print("updated  now added ", process.quantity)

        except Exception as e:
            process = ProcessStore.objects.create(batch=instance, quantity=instance.totalVolume, expDate=instance.expDate,
                                      currentQuantity=instance.totalVolume)
            print("now create-----------------post save ", process.quantity)

    # else:
    #     print("-------------------------------------end-----------------------------------------start",instance.totalVolume)

