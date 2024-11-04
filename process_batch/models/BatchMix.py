from django.db import models
from django.db.models import Avg
from django.utils import timezone
from inventory.models import Material, GoodsReturnNote
from process_batch.models.BatchMixIceCream import BatchMixIceCreamTemplate
from process_batch.models.categories import BatchMixSubCategory


class BatchMix(models.Model):
    batchName = models.CharField(max_length=100)
    batchCode = models.CharField(max_length=100)
    batchDate = models.DateField()
    expDate = models.DateField(null=True, blank=True)
    subCategory = models.ForeignKey(BatchMixSubCategory, on_delete=models.CASCADE)
    totalVolume = models.FloatField(max_length=20)

    is_deleted = models.BooleanField(default=False)
    is_expired=models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.batchName)

    def is_expired_check(self):
        return self.expDate < timezone.now().date()
    # class Meta:
    #     verbose_name_plural = "BatchMix"

    @property
    def total_ingredient_cost(self):
        return round((sum(ing.Ingredient_amount for ing in self.batch_mix_ingredients.all())),2)

    @property
    def cost_per_liter(self):
        return round((self.total_ingredient_cost / self.totalVolume if self.totalVolume > 0 else 0),2)

    @property
    def cost_per_kg(self):
        try:
            # templates = BatchMixIceCreamTemplate.objects.filter(subCategory=self.subCategory)
            templates = BatchMixIceCreamTemplate.objects.filter(subCategory=self.subCategory)
            if not templates.exists():
                print("No related BatchMixIceCreamTemplate found for this subCategory")
                return 0

            # Use the average standard_conversion_factor if multiple templates exist
            avg_conversion_factor = templates.aggregate(Avg('standard_converstion_factor'))[
                'standard_converstion_factor__avg']

            if self.totalVolume > 0 and avg_conversion_factor > 0:
                total_weight = (self.totalVolume * avg_conversion_factor)
                return round(self.total_ingredient_cost / total_weight,2)
            return 0
        except Exception as e:
            print(f"Error calculating cost per kg: {str(e)}")
            return 0

class BatchMixIngredients(models.Model):
    SyrupBatchMix = models.ForeignKey(BatchMix, on_delete=models.CASCADE,related_name='batch_mix_ingredients')
    ingredient = models.ForeignKey(Material, on_delete=models.CASCADE,related_name="batch_mix_ingredient",null=True,blank=True)
    ingredient_process_store=models.ManyToManyField('process_store.ProcessStore',related_name="batch_mix_ingredient_process")
    percentage = models.FloatField(max_length=20)
    quantity = models.FloatField(max_length=20)
    grnlist = models.JSONField(default=list)

    rate = models.FloatField(max_length=20, default=0.0)

    is_deleted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.SyrupBatchMix.batchName)

    # class Meta:
    #     verbose_name_plural = "BatchMixIngredients"
    @property
    def process_store_names(self):
        # Collect names from related ProcessStore objects
        process_store_names = [store.batch.batchName for store in self.ingredient_process_store.all()]
        return ', '.join(process_store_names) if process_store_names else "No Process Stores"
    @property
    def process_store_id(self):
        # Collect names from related ProcessStore objects
        process_store_names = [store.id for store in self.ingredient_process_store.all()]
        return ', '.join(process_store_names) if process_store_names else "No Process Stores"
    @property
    def process_store_Batch(self):
        # Collect names from related ProcessStore objects
        process_store_names = [store.batch.batchCode for store in self.ingredient_process_store.all()]
        return process_store_names

    @property
    def Ingredient_amount(self):
        amount = 0
        try:
            # Get the GRN data for the ingredient
            grn_data = GoodsReturnNote.objects.filter(materialName_id=self.ingredient.id).values('approvedQuantity','approvedPrice').last()

            if grn_data:
                approved_quantity = grn_data.get('approvedQuantity', 0)
                approved_price = grn_data.get('approvedPrice', 0)

                # print(f"Approved Quantity: {approved_quantity} | Approved Price: {approved_price}")

                # Calculate the approved rate
                if approved_quantity > 0:
                    approved_rate = approved_price / approved_quantity
                    # print(f"Approved Rate: {approved_rate}")
                else:
                    # print(f"Warning: Approved quantity is 0 or less for ingredient {self.ingredient.materialName}")
                    approved_rate = 0

                # Check for Milk and apply specific logic
                if self.ingredient.materialName == "Milk":
                    # print(self.quantity,'-----------quantity ')
                    amount = (self.quantity / 1.03) * approved_rate
                    # print(f"Milk Ingredient Amount: {amount}")
                else:
                    amount = self.quantity * approved_rate
                    # print(f"Non-Milk Ingredient Amount: {amount}")
            else:
                print(f"No GRN data found for ingredient {self.ingredient.materialName}")
            print("-----------------------------------------------------------------")
            print("amount",amount)
            print("-----------------------------------------------------------------")
            return amount
        except:
            return 0


# =======================

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.db import transaction

def generate_unique_batch_code(base_code):
    with transaction.atomic():
        latest_batch = BatchMix.objects.filter(
            batchCode__startswith=base_code
        ).order_by('-batchCode').first()

        if latest_batch:
            # Extract the serial number from the latest batch code
            last_serial_number = int(latest_batch.batchCode.split('-')[-1])
            serial_number = last_serial_number + 1
        else:
            # Start with 1 if no batches exist for this base code
            serial_number = 1

        # Format the serial number to ensure it's always 3 digits
        formatted_serial = f"{serial_number:03d}"

        # Create the new unique batch code
        new_batch_code = f"{base_code}-{formatted_serial}"

        # Ensure uniqueness
        while BatchMix.objects.filter(batchCode=new_batch_code).exists():
            serial_number += 1
            formatted_serial = f"{serial_number:03d}"
            new_batch_code = f"{base_code}-{formatted_serial}"

    return new_batch_code

@receiver(pre_save, sender=BatchMix)
def update_batch_code(sender, instance, **kwargs):
    if not instance.pk:  # New instance
        current_datetime = now()
        current_date = current_datetime.strftime("%m%d%Y")  # Format: Month-Day-Year
        base_code = f"{instance.batchCode}-{current_date}"
        instance.batchCode = generate_unique_batch_code(base_code)
        print("New instance", instance.batchCode)
    else:  # Existing instance
        try:
            old_instance = BatchMix.objects.get(pk=instance.pk)
            if old_instance.batchCode != instance.batchCode:
                # The batch code has been manually changed
                parts = instance.batchCode.split('-')
                if len(parts) >= 2:
                    new_prefix = parts[0]
                    old_date = old_instance.batchCode.split('-')[1]
                    base_code = f"{new_prefix}-{old_date}"
                    instance.batchCode = generate_unique_batch_code(base_code)
                    print("Updated instance", instance.batchCode)
                else:
                    # If the manually entered batch code doesn't have the expected format,
                    # we'll treat it as a new batch code
                    current_datetime = now()
                    current_date = current_datetime.strftime("%m%d%Y")
                    base_code = f"{instance.batchCode}-{current_date}"
                    instance.batchCode = generate_unique_batch_code(base_code)
                    print("Updated instance with new format", instance.batchCode)
        except BatchMix.DoesNotExist:
            # This shouldn't happen, but if it does, treat it as a new instance
            current_datetime = now()
            current_date = current_datetime.strftime("%m%d%Y")
            base_code = f"{instance.batchCode}-{current_date}"
            instance.batchCode = generate_unique_batch_code(base_code)
            print("New instance (exception case)", instance.batchCode)
# =======================
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
# from django.utils.timezone import now
# from django.db import transaction
#
#
# def generate_unique_batch_code(instance, is_new=True):
#     if is_new:
#         # For new instances, use current date
#         current_datetime = now()
#         current_date = current_datetime.strftime("%m%d%Y")  # Format: Month-Day-Year
#         base_code = f"{instance.batchCode}-{current_date}"
#     else:
#         # For updates, keep the existing date
#         base_code = instance.batchCode
#
#     # Find the highest serial number for this base code
#     with transaction.atomic():
#         latest_batch = BatchMix.objects.filter(
#             batchCode__startswith=base_code
#         ).order_by('-batchCode').first()
#
#         if latest_batch:
#             # Extract the serial number from the latest batch code
#             last_serial_number = int(latest_batch.batchCode.split('-')[-1])
#             serial_number = last_serial_number + 1
#         else:
#             # Start with 1 if no batches exist for this base code
#             serial_number = 1
#
#         # Format the serial number to ensure it's always 3 digits
#         formatted_serial = f"{serial_number:03d}"
#
#         # Create the new unique batch code
#         new_batch_code = f"{base_code}-{formatted_serial}"
#
#         # Ensure uniqueness
#         while BatchMix.objects.filter(batchCode=new_batch_code).exists():
#             serial_number += 1
#             formatted_serial = f"{serial_number:03d}"
#             new_batch_code = f"{base_code}-{formatted_serial}"
#
#     return new_batch_code
#
#
# @receiver(pre_save, sender=BatchMix)
# def update_batch_code(sender, instance, **kwargs):
#     if not instance.pk:  # New instance
#         instance.batchCode = generate_unique_batch_code(instance, is_new=True)
#         print("New instance",instance.batchCode)
#
#
# @receiver(post_save, sender=BatchMix)
# def post_save_update_batch_code(sender, instance, created, **kwargs):
#     if not created:  # This is an update
#         old_instance = BatchMix.objects.get(pk=instance.pk)
#         if old_instance.batchCode != instance.batchCode:
#             # The batch code prefix has been manually changed
#             # Keep the date from the old batch code
#             old_date = old_instance.batchCode.split('-')[1]
#             new_prefix = instance.batchCode.split('-')[0]
#             base_code = f"{new_prefix}-{old_date}"
#
#             # Generate a new unique batch code with the updated prefix and old date
#             instance.batchCode = generate_unique_batch_code(instance, is_new=False)
#             instance.save()
#             print("Update instance", instance.batchCode)
# from django.db.models.signals import pre_save
# from django.dispatch import receiver
# from django.utils.timezone import now
# from django.db import transaction
#
# def generate_unique_batch_code(instance):
#     current_datetime = now()
#     current_date = current_datetime.strftime("%m%d%Y")  # Format: Month-Day-Year
#
#     # Base batch code
#     base_code = f"{instance.batchCode}-{current_date}"
#
#     # Find the highest serial number for today
#     with transaction.atomic():
#         latest_batch = BatchMix.objects.filter(
#             batchCode__startswith=base_code
#         ).order_by('-batchCode').first()
#
#         if latest_batch:
#             # Extract the serial number from the latest batch code
#             last_serial_number = int(latest_batch.batchCode.split('-')[-1])
#             serial_number = last_serial_number + 1
#         else:
#             # Start with 1 if no batches exist for today
#             serial_number = 1
#
#         # Format the serial number to ensure it's always 3 digits
#         formatted_serial = f"{serial_number:03d}"
#
#         # Create the new unique batch code
#         new_batch_code = f"{base_code}-{formatted_serial}"
#
#         # Ensure uniqueness
#         while BatchMix.objects.filter(batchCode=new_batch_code).exists():
#             serial_number += 1
#             formatted_serial = f"{serial_number:03d}"
#             new_batch_code = f"{base_code}-{formatted_serial}"
#
#     return new_batch_code
#
# @receiver(pre_save, sender=BatchMix)
# def update_batch_code(sender, instance, **kwargs):
#     if not instance.pk:  # Only update when a new instance is created
#         instance.batchCode = generate_unique_batch_code(instance)


# =======================
#
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils.timezone import now
#
#
# @receiver(post_save, sender=BatchMix)
# def update_batch_code(sender, instance, created, **kwargs):
#     if created:  # Only update when a new instance is created
#         current_datetime = now()
#         current_date = current_datetime.strftime("%m%d%Y")  # Format: Month-Day-Year
#
#         # Get the latest batch for today
#         latest_batch_for_today = BatchMix.objects.filter(
#             batchCode__contains=current_date
#         ).order_by('-batchCode').first()
#
#         if latest_batch_for_today:
#             # Extract the serial number from the latest batch code
#             last_serial_number = int(latest_batch_for_today.batchCode.split('-')[-1])
#             serial_number = last_serial_number + 1
#         else:
#             # Start with 1 if no batches exist for today
#             serial_number = 1
#
#         # Format the serial number to ensure it's always 3 digits
#         formatted_serial = f"{serial_number:03d}"
#
#         # Update the batch code with the new serial number
#         instance.batchCode = f"{instance.batchCode}-{current_date}-{formatted_serial}"
#         instance.save(update_fields=['batchCode'])  # Save only the batchCode field
#         # print(instance.batchCode, '-------------data saved')

"""
from django.db import models
from django.db.models import Avg

from inventory.models import Material, GoodsReturnNote
from process_batch.models.BatchMixIceCream import BatchMixIceCreamTemplate
from process_batch.models.categories import BatchMixSubCategory


class BatchMix(models.Model):
    batchName = models.CharField(max_length=100)
    batchCode = models.CharField(max_length=100)
    batchDate = models.DateField()
    expDate = models.DateField(null=True, blank=True)
    subCategory = models.ForeignKey(BatchMixSubCategory, on_delete=models.CASCADE)
    totalVolume = models.FloatField(max_length=20)

    is_deleted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.batchName)

    # class Meta:
    #     verbose_name_plural = "BatchMix"

    @property
    def total_ingredient_cost(self):
        return round((sum(ing.Ingredient_amount for ing in self.batch_mix_ingredients.all())),2)

    @property
    def cost_per_liter(self):
        return round((self.total_ingredient_cost / self.totalVolume if self.totalVolume > 0 else 0),2)

    @property
    def cost_per_kg(self):
        try:
            # templates = BatchMixIceCreamTemplate.objects.filter(subCategory=self.subCategory)
            templates = BatchMixIceCreamTemplate.objects.filter(subCategory=self.subCategory)
            if not templates.exists():
                print("No related BatchMixIceCreamTemplate found for this subCategory")
                return 0

            # Use the average standard_conversion_factor if multiple templates exist
            avg_conversion_factor = templates.aggregate(Avg('standard_converstion_factor'))[
                'standard_converstion_factor__avg']

            if self.totalVolume > 0 and avg_conversion_factor > 0:
                total_weight = (self.totalVolume * avg_conversion_factor)
                return round(self.total_ingredient_cost / total_weight,2)
            return 0
        except Exception as e:
            print(f"Error calculating cost per kg: {str(e)}")
            return 0

class BatchMixIngredients(models.Model):
    # added post signal to signals.py
    SyrupBatchMix = models.ForeignKey(BatchMix, on_delete=models.CASCADE,related_name='batch_mix_ingredients')
    ingredient = models.ForeignKey(Material, on_delete=models.CASCADE,related_name="batch_mix_ingredient",null=True,blank=True)
    ingredient_process_store=models.ManyToManyField('process_store.ProcessStore',related_name="batch_mix_ingredient_process")
    percentage = models.FloatField(max_length=20)
    quantity = models.FloatField(max_length=20)
    grnlist = models.JSONField(default=list)

    rate = models.FloatField(max_length=20, default=0.0)

    is_deleted = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.SyrupBatchMix.batchName)

    # class Meta:
    #     verbose_name_plural = "BatchMixIngredients"
    @property
    def process_store_names(self):
        # Collect names from related ProcessStore objects
        process_store_names = [store.batch.batchName for store in self.ingredient_process_store.all()]
        return ', '.join(process_store_names) if process_store_names else "No Process Stores"
    @property
    def process_store_id(self):
        # Collect names from related ProcessStore objects
        process_store_names = [store.id for store in self.ingredient_process_store.all()]
        return ', '.join(process_store_names) if process_store_names else "No Process Stores"
    @property
    def process_store_Batch(self):
        # Collect names from related ProcessStore objects
        process_store_names = [store.batch.batchCode for store in self.ingredient_process_store.all()]
        return process_store_names

    @property
    def Ingredient_amount(self):
        amount = 0
        try:
            # Get the GRN data for the ingredient
            grn_data = GoodsReturnNote.objects.filter(materialName_id=self.ingredient.id).values('approvedQuantity','approvedPrice').last()

            if grn_data:
                approved_quantity = grn_data.get('approvedQuantity', 0)
                approved_price = grn_data.get('approvedPrice', 0)

                # print(f"Approved Quantity: {approved_quantity} | Approved Price: {approved_price}")

                # Calculate the approved rate
                if approved_quantity > 0:
                    approved_rate = approved_price / approved_quantity
                    # print(f"Approved Rate: {approved_rate}")
                else:
                    # print(f"Warning: Approved quantity is 0 or less for ingredient {self.ingredient.materialName}")
                    approved_rate = 0

                # Check for Milk and apply specific logic
                if self.ingredient.materialName == "Milk":
                    # print(self.quantity,'-----------quantity ')
                    amount = (self.quantity / 1.03) * approved_rate
                    # print(f"Milk Ingredient Amount: {amount}")
                else:
                    amount = self.quantity * approved_rate
                    # print(f"Non-Milk Ingredient Amount: {amount}")
            else:
                print(f"No GRN data found for ingredient {self.ingredient.materialName}")
            print("-----------------------------------------------------------------")
            print("amount",amount)
            print("-----------------------------------------------------------------")
            return amount
        except:
            return 0


# ==========================


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now


@receiver(post_save, sender=BatchMix)
def update_batch_code(sender, instance, created, **kwargs):
    if created:  # Only update when a new instance is created
        current_datetime = now()
        current_date = current_datetime.strftime("%m%d%Y")  # Format: Month-Day-Year

        # Get the latest batch for today
        latest_batch_for_today = BatchMix.objects.filter(
            batchCode__contains=current_date
        ).order_by('-batchCode').first()

        if latest_batch_for_today:
            # Extract the serial number from the latest batch code
            last_serial_number = int(latest_batch_for_today.batchCode.split('-')[-1])
            serial_number = last_serial_number + 1
        else:
            # Start with 1 if no batches exist for today
            serial_number = 1

        # Format the serial number to ensure it's always 3 digits
        formatted_serial = f"{serial_number:03d}"

        # Update the batch code with the new serial number
        instance.batchCode = f"{instance.batchCode}-{current_date}-{formatted_serial}"
        instance.save(update_fields=['batchCode'])  # Save only the batchCode field
        # print(instance.batchCode, '-------------data saved')


"""