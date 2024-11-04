from django.db import models, transaction
from django.db.models import Max
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from accounts.models import UserBase
from products.models import Product
from django.utils import timezone


class ProductStockRecord(models.Model):
    """
    Represents a detailed stock record for a product, including production, sales, and closing stock information.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_records')
    stock_record = models.ForeignKey("StockRecord", on_delete=models.CASCADE, related_name='product_stock_records')
    volume_nos = models.FloatField(default=0.0)
    mrp = models.FloatField(default=0.0)
    lit_factor = models.FloatField(default=0.0)

    opening_stock_units=models.FloatField(default=0.0)
    opening_stock_lits=models.FloatField(default=0.0)
    opening_stock_value=models.FloatField(default=0.0)

    production_units = models.FloatField(default=0.0)
    production_lits = models.FloatField(default=0.0)
    production_value = models.FloatField( default=0.0)

    sales_units = models.FloatField(default=0.0)
    sales_lits = models.FloatField(default=0.0)
    sales_value = models.FloatField(default=0.0)

    closing_stock_units = models.FloatField(default=0.0)
    closing_stock_lits = models.FloatField(default=0.0)
    closing_stock_value = models.FloatField(default=0.0)

    damage_in_units=models.FloatField(default=0.0)
    return_in_units=models.FloatField(default=0.0)

    physical_stock = models.FloatField(default=0.0)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the product was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when the product was last updated")

    def __str__(self):
        return f'Stock Record for {self.product.product_name} - {self.id}'

    class Meta:
        unique_together = ('product', 'stock_record')


class OpeningStock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE,related_name='opening_stock')
    opening_stock = models.FloatField(default=0.0)
    closing_stock = models.FloatField(default=0.0)
    physical_stock = models.FloatField(default=0.0)

    def __str__(self):
        return self.product.product_name


class StockRecord(models.Model):
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add a FileField for storing generated files like PDFs
    generated_file = models.FileField(upload_to='stock_reports/', blank=True, null=True)
    is_editable = models.BooleanField(default=True)  # New field to control editability

    def __str__(self):
        return f'Stock Record {self.id}'

    class Meta:
        ordering = ['-date', '-created_at']  # Order by date and creation time descending

    @classmethod
    def get_latest_editable(cls):
        today = timezone.now().date()
        latest_record = cls.objects.first()
        if latest_record and latest_record.date < today:
            print(f"DEBUG: Latest editable record found: {latest_record}")
            return latest_record
        print("DEBUG: No editable record found")
        return None
# ===============
@receiver(pre_delete, sender=StockRecord)
def prepare_stock_record_deletion(sender, instance, **kwargs):
    # Store the data we need for post-deletion processing
    instance._previous_record = StockRecord.objects.filter(date__lt=instance.date).order_by('-date').first()
    instance._product_stock_records = list(instance.product_stock_records.all())

@receiver(post_delete, sender=StockRecord)
def update_opening_stocks(sender, instance, **kwargs):
    with transaction.atomic():
        for product_stock_record in instance._product_stock_records:
            opening_stock, created = OpeningStock.objects.get_or_create(product=product_stock_record.product)

            if instance._previous_record:
                previous_product_record = instance._previous_record.product_stock_records.filter(
                    product=product_stock_record.product
                ).first()
                if previous_product_record:
                    opening_stock.opening_stock = previous_product_record.opening_stock_units
                    opening_stock.closing_stock = previous_product_record.closing_stock_units-previous_product_record.damage_in_units+previous_product_record.return_in_units
                    opening_stock.physical_stock = previous_product_record.physical_stock
                    print("updtaed ,'==============here ")
            else:
                # If no previous record, set to zero or some default value
                opening_stock.opening_stock = 0
                opening_stock.closing_stock = 0
                opening_stock.physical_stock = 0

            opening_stock.save()
# ===============
@receiver(post_save, sender=StockRecord)
def update_stock_record_editability(sender, instance, created, **kwargs):
    today = timezone.now().date()

    with transaction.atomic():
        # Set all records to non-editable
        StockRecord.objects.all().update(is_editable=False)

        # Get the most recent record
        most_recent = StockRecord.objects.aggregate(Max('date'))['date__max']

        if most_recent:
            # Make the most recent record editable
            StockRecord.objects.filter(date=most_recent).update(is_editable=True)

        # If the current instance is for today and it's not the most recent, make it editable
        if instance.date == today and instance.date != most_recent:
            instance.is_editable = True
            instance.save()

    # Debug output
    print(f"DEBUG: Signal triggered for StockRecord {instance.id}, created: {created}")
    print(f"DEBUG: Most recent record date: {most_recent}")
    print("DEBUG: Final edit ability state:")
    for record in StockRecord.objects.all().order_by('-date'):
        print(f"Record {record.id}, Date: {record.date}, Editable: {record.is_editable}")
# @receiver(post_save, sender=StockRecord)
# def update_stock_record_editability(sender, instance, created, **kwargs):
#     today = timezone.now().date()
#     print(f"DEBUG: Signal triggered for StockRecord {instance.id}, created: {created}")
#
#     if created:
#         print(f"DEBUG: New record created for date: {instance.date}")
#         if instance.date == today:
#             print("DEBUG: New record is for today, updating other records")
#             StockRecord.objects.exclude(id=instance.id).update(is_editable=False)
#             instance.is_editable = True
#             instance.save()
#         else:
#             print("DEBUG: New record is not for today, updating edit ability")
#             StockRecord.objects.all().update(is_editable=False)
#             latest_editable = StockRecord.get_latest_editable()
#             if latest_editable:
#                 latest_editable.is_editable = True
#                 latest_editable.save()
#     else:
#         print("DEBUG: Existing record updated, recalculating edit ability")
#         StockRecord.objects.all().update(is_editable=False)
#         latest_editable = StockRecord.get_latest_editable()
#         if latest_editable:
#             latest_editable.is_editable = True
#             latest_editable.save()
#
#     print("DEBUG: Final edit ability state:")
#     for record in StockRecord.objects.all():
#         print(f"Record {record.id}, Date: {record.date}, Editable: {record.is_editable}")
# </editor-fold>




# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.db import transaction
# from .models import StockRecord
#
# @receiver(post_save, sender=StockRecord)
# def update_stock_record_editability(sender, instance, created, **kwargs):
#     if hasattr(instance, '_editability_updated'):
#         return
#
#     print(f"\n--- Signal triggered for StockRecord {instance.id} ---")
#     print(f"Is this a new record? {created}")
#     print(f"Current record date: {instance.date}")
#     print(f"Current record editability: {instance.is_editable}")
#
#     with transaction.atomic():
#         if created:
#             print("New record created. Making all existing records non-editable...")
#             updated_count = StockRecord.objects.filter(date__lt=instance.date).update(is_editable=False)
#             print(f"Updated {updated_count} existing records to non-editable")
#
#             print("Setting new record as editable...")
#             StockRecord.objects.filter(id=instance.id).update(is_editable=True)
#             print(f"New record {instance.id} is now editable")
#         else:
#             print("Existing record updated. Checking if it's the latest...")
#             latest_record = StockRecord.objects.order_by('-date').first()
#             print(f"Latest record id: {latest_record.id}, date: {latest_record.date}")
#
#             if latest_record.id == instance.id:
#                 print("Updated record is the latest. Making it the only editable record...")
#                 updated_count = StockRecord.objects.exclude(id=instance.id).update(is_editable=False)
#                 print(f"Updated {updated_count} records to non-editable")
#
#                 StockRecord.objects.filter(id=instance.id).update(is_editable=True)
#                 print(f"Record {instance.id} is now the only editable record")
#             else:
#                 print("Updated record is not the latest. Ensuring it's not editable...")
#                 StockRecord.objects.filter(id=instance.id).update(is_editable=False)
#                 print(f"Record {instance.id} is now non-editable")
#
#                 print("Ensuring the latest record is editable...")
#                 StockRecord.objects.filter(id=latest_record.id).update(is_editable=True)
#                 print(f"Latest record {latest_record.id} is now editable")
#
#     instance._editability_updated = True
#
#     print("--- Final state ---")
#     for record in StockRecord.objects.order_by('-date'):
#         print(f"Record {record.id}: date={record.date}, is_editable={record.is_editable}")
#     print("--- End of signal execution ---\n")




# @receiver(post_save, sender=StockRecord)
# def update_stock_record_editability(sender, instance, created, **kwargs):
#     print(f"\n--- Signal triggered for StockRecord {instance.id} ---")
#     print(f"Is this a new record? {created}")
#     print(f"Current record date: {instance.date}")
#     print(f"Current record editability: {instance.is_editable}")
#
#     if created:
#         print("New record created. Making all existing records non-editable...")
#         updated_count = StockRecord.objects.filter(date__lt=instance.date).update(is_editable=False)
#         print(f"Updated {updated_count} existing records to non-editable")
#
#         print("Setting new record as editable...")
#         instance.is_editable = True
#         instance.save()
#         print(f"New record {instance.id} is now editable")
#     else:
#         print("Existing record updated. Checking if it's the latest...")
#         latest_record = StockRecord.objects.order_by('-date').first()
#         print(f"Latest record id: {latest_record.id}, date: {latest_record.date}")
#
#         if latest_record == instance:
#             print("Updated record is the latest. Making it the only editable record...")
#             updated_count = StockRecord.objects.exclude(id=instance.id).update(is_editable=False)
#             print(f"Updated {updated_count} records to non-editable")
#
#             instance.is_editable = True
#             instance.save()
#             print(f"Record {instance.id} is now the only editable record")
#         else:
#             print("Updated record is not the latest. Ensuring it's not editable...")
#             instance.is_editable = False
#             instance.save()
#             print(f"Record {instance.id} is now non-editable")
#
#             print("Ensuring the latest record is editable...")
#             latest_record.is_editable = True
#             latest_record.save()
#             print(f"Latest record {latest_record.id} is now editable")
#
#     print("--- Final state ---")
#     for record in StockRecord.objects.order_by('-date'):
#         print(f"Record {record.id}: date={record.date}, is_editable={record.is_editable}")
#     print("--- End of signal execution ---\n")

# @receiver(post_save, sender=StockRecord)
# def update_stock_record_editability(sender, instance, created, **kwargs):
#     print(f"\n--- Signal triggered for StockRecord {instance.id} ---")
#     print(f"Is this a new record? {created}")
#     print(f"Current record date: {instance.date}")
#     print(f"Current record editability: {instance.is_editable}")
#
#     if created:
#         print("New record created. Making all existing records non-editable...")
#         updated_count = StockRecord.objects.filter(user=instance.user).update(is_editable=False)
#         print(f"Updated {updated_count} existing records to non-editable")
#
#         print("Setting new record as editable...")
#         instance.is_editable = True
#         instance.save()
#         print(f"New record {instance.id} is now editable")
#     else:
#         print("Existing record updated. Checking if it's the latest...")
#         latest_record = StockRecord.objects.filter(user=instance.user).order_by('-date').first()
#         print(f"Latest record id: {latest_record.id}, date: {latest_record.date}")
#
#         if latest_record == instance:
#             print("Updated record is the latest. Making it the only editable record...")
#             updated_count = StockRecord.objects.filter(user=instance.user).update(is_editable=False)
#             print(f"Updated {updated_count} records to non-editable")
#
#             instance.is_editable = True
#             instance.save()
#             print(f"Record {instance.id} is now the only editable record")
#         else:
#             print("Updated record is not the latest. Ensuring it's not editable...")
#             instance.is_editable = False
#             instance.save()
#             print(f"Record {instance.id} is now non-editable")
#
#             print("Ensuring the latest record is editable...")
#             latest_record.is_editable = True
#             latest_record.save()
#             print(f"Latest record {latest_record.id} is now editable")
#
#     print("--- Final state ---")
#     for record in StockRecord.objects.filter(user=instance.user).order_by('-date'):
#         print(f"Record {record.id}: date={record.date}, is_editable={record.is_editable}")
#     print("--- End of signal execution ---\n")
