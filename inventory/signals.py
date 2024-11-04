from django.db import transaction, IntegrityError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from process_batch.models import BatchMix
from process_batch.models.BatchMix import BatchMixIngredients
from process_store.models import ProcessStore
from .models import GoodsReturnNote, Store, StoreHistory, StoreGRN


@receiver(post_save, sender=GoodsReturnNote)
def update_store(sender, instance, created, **kwargs):
    if created:
        store_item = Store.objects.filter(
            materialName=instance.materialName,
            typeName=instance.typeName
        ).first()

        if store_item is None:
            # Create a new store item
            store_item = Store.objects.create(
                materialName=instance.materialName,
                typeName=instance.typeName,
                totalQuantity=instance.approvedQuantity,
                currentQuantity=instance.approvedQuantity,
            )
        else:
            # Update the existing store item if necessary
            store_item.totalQuantity = instance.approvedQuantity
            store_item.currentQuantity = instance.approvedQuantity
            store_item.save()
        # store_item, created = Store.objects.get_or_create(
        #     materialName=instance.materialName,
        #     typeName=instance.typeName,
        #     measure=instance.measure,
        #     defaults={
        #         'totalQuantity': instance.approvedQuantity,
        #         'currentQuantity': instance.approvedQuantity,
        #     }
        # )
        try:
            StoreGRN.objects.create(
                store=store_item,
                grn=instance,
                quantity=instance.approvedQuantity
            )
        except Exception as e:
            print("Error in updating store GRN :-"+e)
        if not created:
            store_item.totalQuantity += instance.approvedQuantity
            store_item.currentQuantity += instance.approvedQuantity
            store_item.save()


def use_material(material, type, quantity_used):
    try:
        store_item = Store.objects.get(materialName=material, typeName=type)
        grns_used = []
        if store_item.currentQuantity >= quantity_used:
            store_item.currentQuantity -= quantity_used
            store_item.save()

            StoreHistory.objects.create(
                materialName=material,
                CurrentQuantity=store_item.currentQuantity,
                ConsumedQuantity=quantity_used,
                RemainingQuantity=store_item.currentQuantity
            )
            try:
                remaining_quantity = quantity_used
                store_grns = StoreGRN.objects.filter(store=store_item).order_by('created')

                if store_grns.exists():
                    with transaction.atomic():
                        for store_grn in store_grns:
                            if remaining_quantity <= 0:
                                break
                            if store_grn.quantity > remaining_quantity:
                                store_grn.quantity -= remaining_quantity
                                grns_used.append(store_grn.grn.GRNnumber)
                                store_grn.save()
                                remaining_quantity = 0
                            else:
                                remaining_quantity -= store_grn.quantity
                                store_grn.delete()
                    if remaining_quantity > 0:
                        raise ValueError(
                            "The reduction quantity could not be fully processed. Not enough GRN entries available.")
            except Exception as e:
                print("Error in updating store GRN (signal) while consuming material :-"+e)

            return grns_used
        else:
            raise ValidationError("Not enough quantity in the store")
    except Store.DoesNotExist:
        raise ValidationError("Material not found in the store")


@receiver(pre_save, sender=BatchMixIngredients)
@transaction.atomic
def update_store_on_batch_ingredients_save(sender, instance, **kwargs):
    global old_instance
    print("Signal: update_store_on_batch_ingredients_save", instance)

    # Check if this is a new instance or if the quantity has changed
    if not instance.pk or BatchMixIngredients.objects.filter(pk=instance.pk).exists():
        old_instance = BatchMixIngredients.objects.filter(pk=instance.pk).first()
        if old_instance and old_instance.quantity == instance.quantity:
            print("Quantity unchanged, skipping material use.")
            return

    # Initialize grnlist if it doesn't exist
    if not hasattr(instance, 'grnlist'):
        instance.grnlist = []

    try:
        # Calculate the quantity to be used
        quantity_to_use = instance.quantity
        if old_instance:
            # If updating, only use the difference
            quantity_to_use = instance.quantity - old_instance.quantity

        # Only call use_material if there's a quantity to use
        if quantity_to_use > 0:
            grns_used = use_material(instance.ingredient, instance.ingredient.type, quantity_to_use)
            print("call use material")
            if grns_used is not None:
                instance.grnlist.extend(grns_used)
                print(f"GRNs used: {instance.grnlist}")
        elif quantity_to_use < 0:
            # Handle case where quantity is reduced (might need to implement a return_material function)
            print(f"Quantity reduced by {abs(quantity_to_use)}. Implement return_material if needed.")

    except ValidationError as e:
        raise ValidationError("Not enough quantity in the store")
    except AttributeError as e:
        print(f"AttributeError: {str(e)}. Skipping use_material.")
    except Exception as e:
        print(f"Unexpected error in signal handler: {str(e)}")
        raise

# ==================================



# <editor-fold desc="old">
# @receiver(post_save, sender=GoodsReturnNote)
# def update_store(sender, instance, created, **kwargs):
#     if created:
#         print("-----------here also call-------------store============update store function")
#         try:
#             store_item = Store.objects.create(
#                 materialName=instance.materialName,
#                 typeName=instance.typeName,
#                 measure=instance.measure,
#                 totalQuantity=instance.approvedQuantity,
#                 currentQuantity=instance.approvedQuantity
#             )
#         except IntegrityError:
#             store_item = Store.objects.get(materialName=instance.materialName, typeName=instance.typeName)
#             store_item.currentQuantity += instance.approvedQuantity  # Update current quantity if needed
#             store_item.save()
#
#         try:
#             StoreGRN.objects.create(
#                 store=store_item,
#                 grn=instance,
#                 quantity=instance.approvedQuantity
#             )
#         except Exception as e:
#             print("Error in updating store GRN :-"+e)
#         if not created:
#             store_item.totalQuantity += instance.approvedQuantity
#             store_item.currentQuantity += instance.approvedQuantity
#             store_item.save()
#
# def use_material(material, type, quantity_used):
#     # print("in signals -- use_material---------here call signal ")
#     try:
#         store_item = Store.objects.get(materialName=material, typeName=type)
#         grns_used = []
#         if store_item.currentQuantity >= quantity_used:
#             print(store_item.currentQuantity,'==========Okay=======p==use_material')
#             store_item.currentQuantity -= quantity_used
#             store_item.save()
#             print(store_item.currentQuantity,'==========Okay======u===use_material')
#
#
#             StoreHistory.objects.create(
#                 materialName=material,
#                 CurrentQuantity=store_item.currentQuantity,
#                 ConsumedQuantity=quantity_used,
#                 RemainingQuantity=store_item.currentQuantity
#             )
#             try:
#                 remaining_quantity = quantity_used
#                 store_grns = StoreGRN.objects.filter(store=store_item).order_by('created')
#
#                 if store_grns.exists():
#                     with transaction.atomic():
#                         for store_grn in store_grns:
#                             if remaining_quantity <= 0:
#                                 break
#                             if store_grn.quantity > remaining_quantity:
#                                 store_grn.quantity -= remaining_quantity
#                                 grns_used.append(store_grn.grn.GRNnumber)
#                                 store_grn.save()
#                                 remaining_quantity = 0
#                             else:
#                                 remaining_quantity -= store_grn.quantity
#                                 store_grn.delete()
#                     if remaining_quantity > 0:
#                         raise ValueError(
#                             "The reduction quantity could not be fully processed. Not enough GRN entries available.")
#             except Exception as e:
#                 print("Error in updating store GRN (signal) while consuming material :-"+e)
#
#             return grns_used
#         else:
#             raise ValidationError("Not enough quantity in the store")
#     except Store.DoesNotExist:
#         raise ValidationError("Material not found in the store")
# </editor-fold>

# ======================================================#


# @receiver(pre_save, sender=BatchMixIngredients)
# @transaction.atomic
# def update_store_on_batch_ingredients_save(sender, instance, **kwargs):
#     # print("in signals -- update_store_on_batch_ingredients_save")
#     # print(instance.pk, "instance.pk", '======signal=======')
#
#     # Initialize grnlist if it doesn't exist
#     if not hasattr(instance, 'grnlist'):
#         instance.grnlist = []
#
#     # Process all instances, regardless of whether they're new or existing
#     try:
#         grns_used = use_material(instance.ingredient, instance.ingredient.type, instance.quantity)
#         if grns_used is not None:
#             instance.grnlist.extend(grns_used)
#             print(instance.grnlist, "instance.grnlist")
#     except ValidationError as e:
#         raise ValidationError("Not enough quantity in the store")
#     except AttributeError as e:
#         # Handle cases where ingredient, type, or quantity might be None
#         print(f"AttributeError: {str(e)}. Skipping use_material.")
#     except Exception as e:
#         # Catch any other unexpected errors
#         print(f"Unexpected error in signal handler: {str(e)}")
#         raise


# ======================================================#
# from django.db.models.signals import pre_save
# from django.dispatch import receiver
# from django.db import transaction
# from django.core.exceptions import ValidationError

# @receiver(pre_save, sender=BatchMixIngredients)
# @transaction.atomic
# def update_store_on_batch_ingredients_save(sender, instance, **kwargs):
#     print("in signals -- update_store_on_batch_ingredients_save")
#     print(instance.pk, "instance.pk", '======signal=======')
#
#     # If the instance is new (pk is None), skip processing
#     if instance.pk is None:
#         print("Instance is new, skipping GRN processing.")
#         return
#
#     # Check if ingredient, ingredient.type, and quantity are None; skip if any of them is None
#     if instance.ingredient is None or instance.ingredient.type is None or instance.quantity is None:
#         print("One or more required fields are None, skipping use_material.")
#         return
#
#     # Proceed with the logic if all required fields are valid (not None)
#     try:
#         grns_used = use_material(instance.ingredient, instance.ingredient.type, instance.quantity)
#         if grns_used is not None:
#             if not hasattr(instance, 'grnlist'):
#                 instance.grnlist = []  # Ensure grnlist is initialized
#             instance.grnlist.extend(grns_used)
#             print(instance.grnlist, "instance.grnlist")
#     except ValidationError as e:
#         raise ValidationError("Not enough quantity in the store")


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.db import transaction
# from django.core.exceptions import ValidationError
# #
# @receiver(post_save, sender=BatchMixIngredients)
# @transaction.atomic
# def update_store_on_batch_ingredients_save(sender, instance, **kwargs):
#     print("in signals -- update_store_on_batch_ingredients_save")
#     print(instance.pk, "instance.pk", '======signal=======')
#
#     # Check if ingredient, ingredient.type, and quantity are None; skip if any of them is None
#     if instance.ingredient is None or instance.ingredient.type is None or instance.quantity is None:
#         print("One or more required fields are None, skipping use_material.")
#         return
#
#     # Proceed with the logic if all required fields are valid (not None)
#     try:
#         grns_used = use_material(instance.ingredient, instance.ingredient.type, instance.quantity)
#         if grns_used is not None:
#             if not hasattr(instance, 'grnlist') or instance.grnlist is None:
#                 instance.grnlist = []  # Ensure grnlist is initialized
#             instance.grnlist.extend(grns_used)
#             instance.save()  # Save the instance after modifying the grnlist
#             print(instance.grnlist, "instance.grnlist")
#     except ValidationError as e:
#         raise ValidationError("Not enough quantity in the store")


# @receiver(pre_save, sender=BatchMixIngredients)
# @transaction.atomic
# def update_store_on_batch_ingredients_save(sender, instance, **kwargs):
#     print("in signals -- update_store_on_batch_ingredients_save")
#     print(instance.pk,"instance.pk"'======signal=======,')
#     if instance.pk is None:
#         try:
#             grns_used = use_material(instance.ingredient, instance.ingredient.type, instance.quantity)
#             if grns_used is not None:
#                 instance.grnlist.extend(grns_used)
#                 print(instance.grnlist, "instance.grnlist")
#         except ValidationError as e:
#             raise ValidationError("Not enough quantity in the store")



# @receiver(pre_save, sender=BatchMixIngredients)
# @transaction.atomic
# def update_store_on_batch_ingredients_save(sender, instance, **kwargs):
#     print("in signals -- update_store_on_batch_ingredients_save")
#     print(instance.pk,"instance.pk"'=====here batch mix then =signal=======,')
#     if instance.pk is None:
#         try:
#             grns_used = use_material(instance.ingredient, instance.ingredient.type, instance.quantity)
#             if grns_used is not None:
#                 instance.grnlist.extend(grns_used)
#                 print(instance.grnlist, "instance.grnlist")
#         except ValidationError as e:
#             raise ValidationError("Not enough quantity in the store")
#

# ===============

# post_save.connect(update_store, sender=GoodsReturnNote)
# pre_save.connect(update_store_on_batch_ingredients_save, sender=BatchIngredients)
# pre_save.connect(update_store_on_batch_ingredients_save, sender=SyrupBatchMixIngredients)

