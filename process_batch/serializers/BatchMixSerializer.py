from datetime import date

from django.db import transaction
from django.forms import model_to_dict
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from inventory.models import Material, Store, GoodsReturnNote, StoreGRN
from inventory.view.Material import material
from process_batch.models.BatchMix import BatchMix, BatchMixIngredients
from process_batch.models.BatchMixIceCream import BatchMixIceCreamTemplate
from process_batch.models.batchMixTemplate import BatchMixTemplateIngredients
from process_store.models import ProcessStore


# <editor-fold desc="getting data batch mix">
#
# Serializer for the Material model
class BatchMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


# Serializer for the BatchMixIngredients model
class BatchMixIngredientsSerializer(serializers.ModelSerializer):
    ingredient = BatchMaterialSerializer()  # This will include the full Material data
    grnlist = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = BatchMixIngredients
        fields = '__all__'

    def get_grnlist(self, obj):
        # Initialize an empty list to store valid GRN values
        valid_grnlist = []

        # Check if obj has a grnlist attribute and that it's not None or empty
        if not hasattr(obj, 'grnlist') or obj.grnlist is None or not obj.grnlist:
            # If grnlist is absent, get batchCodes from ingredient_process_store
            valid_grnlist = [x.batch.batchCode for x in obj.ingredient_process_store.all()]
        else:
            # Handle grnlist based on its type
            if isinstance(obj.grnlist, list):
                for grn in obj.grnlist:
                    if isinstance(grn, dict):
                        print(grn, '=========here i need grn grnlist')
                        # You may want to extract a specific key from the dictionary
                        # For example, if you want to extract 'batchCode'
                        if 'batchCode' in grn:
                            valid_grnlist.append(grn['batchCode'])
                    else:
                        valid_grnlist.append(grn)

            elif isinstance(obj.grnlist, str):
                # If grnlist is a string, split it and get unique GRN values
                grnlist = [grn.strip() for grn in obj.grnlist.split(',') if grn.strip()]
                valid_grnlist.extend(grnlist)

        # Return a list of unique values
        return list(set(valid_grnlist))


# Serializer for the BatchMix model
class GetBatchMixSerializer(serializers.ModelSerializer):
    ingredients = BatchMixIngredientsSerializer(many=True,read_only=True,source="batch_mix_ingredients")  # Note the use of `many=True` since it's a one-to-many relationship

    class Meta:
        model = BatchMix
        fields = '__all__'


# </editor-fold>

# <editor-fold desc="create batch mix">

class batchMixGetProcessStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStore
        fields = '__all__'

class GetDetailBatchMixSerializers(serializers.ModelSerializer):
    class Meta:
        model = BatchMix
        fields = '__all__'

class BatchMixIngredientsSerializer(serializers.ModelSerializer):
    material_name = serializers.SerializerMethodField()
    grnlist_as_dict = serializers.SerializerMethodField(read_only=True)
    ingredient= serializers.SerializerMethodField()

    def get_ingredient(self, obj):
        # Check if the 'ingredient' (Material) exists
        if obj.ingredient:
            return obj.ingredient.id

        # If 'ingredient' does not exist, check if there are any 'ingredient_process_store' entries
        if obj.ingredient_process_store.exists():
            # Retrieve the IDs from the related ProcessStore objects
            process_store_ids = [store.id for store in obj.ingredient_process_store.all()]
            print(process_store_ids,'--------------id')
            return process_store_ids[0]

        return None  # Or return an appropriate default value if needed

    class Meta:
        model = BatchMixIngredients
        fields = ['ingredient',
                  'percentage',
                  'quantity',
                  'rate',
                  'is_deleted',
                  'created',
                  'updated',
                  'material_name',
                  # 'grnlist',
                  'grnlist_as_dict']

    def get_material_name(self, obj):
        material = None

        # Check if the 'ingredient' (Material) exists
        if obj.ingredient:
            material = obj.ingredient.materialName
        if obj.ingredient_process_store.exists():
            # Retrieve the names from the related ProcessStore objects
            material =obj.process_store_names

        return material or "Unknown Material"

    def get_grnlist_as_dict(self, obj):
        if not hasattr(obj, 'grnlist') or obj.grnlist is None or not obj.grnlist:
            return {i: x.batch.batchCode for i, x in enumerate(obj.ingredient_process_store.all())}

        if isinstance(obj.grnlist, list):
            # Ensure grnlist items are hashable (e.g., if they are dicts, convert to tuples)
            hashable_grnlist = []
            for grn in obj.grnlist:
                if isinstance(grn, dict):
                    print(grn,'=========here i need grn grnlist')
                    pass
                    # hashable_grnlist.append(tuple(grn.items()))  # Convert dict to tuple
                else:
                    hashable_grnlist.append(grn)

            # Get the first (and only) unique GRN
            unique_grn = next(iter(set(hashable_grnlist)), None)
            return {0: unique_grn} if unique_grn else {}

        elif isinstance(obj.grnlist, str):
            # If grnlist is a string, split it and get the first unique GRN
            grnlist = [grn.strip() for grn in obj.grnlist.split(',') if grn.strip()]
            unique_grn = next(iter(set(grnlist)), None)
            return {0: unique_grn} if unique_grn else {}

        else:
            return {}

    # def get_grnlist_as_dict(self, obj):
    #     if not hasattr(obj, 'grnlist') or obj.grnlist is None or not obj.grnlist:
    #         return {i: x.batch.batchCode for i, x in enumerate(obj.ingredient_process_store.all())}
    #
    #     if isinstance(obj.grnlist, list):
    #         # Handle list of dictionaries or strings
    #         result = {}
    #         for i, item in enumerate(obj.grnlist):
    #             if isinstance(item, dict):
    #                 # Assuming each dict has a 'grn' key
    #                 result[i] = item.get('grn', '')
    #             elif isinstance(item, str):
    #                 result[i] = item
    #             else:
    #                 # Skip items that are neither dict nor str
    #                 continue
    #         return result
    #     elif isinstance(obj.grnlist, str):
    #         # If grnlist is a string, split it and get unique GRNs
    #         grnlist = [grn.strip() for grn in obj.grnlist.split(',') if grn.strip()]
    #         return {i: grn for i, grn in enumerate(set(grnlist))}
    #     else:
    #         return {}
    # def get_grnlist_as_dict(self, obj):
    #     if not hasattr(obj, 'grnlist') or obj.grnlist is None or not obj.grnlist:
    #         return {i: x.batch.batchCode for i, x in enumerate(obj.ingredient_process_store.all())}
    #
    #     if isinstance(obj.grnlist, list):
    #         # Get the first (and only) unique GRN
    #         unique_grn = next(iter(set(obj.grnlist)), None)
    #         return {0: unique_grn} if unique_grn else {}
    #     elif isinstance(obj.grnlist, str):
    #         # If grnlist is a string, split it and get the first unique GRN
    #         grnlist = [grn.strip() for grn in obj.grnlist.split(',') if grn.strip()]
    #         unique_grn = next(iter(set(grnlist)), None)
    #         return {0: unique_grn} if unique_grn else {}
    #     else:
    #         return {}
    # def get_grnlist_as_dict(self, obj):
    #     print("object", obj.grnlist)
    #     if obj.grnlist is None:
    #
    #         return {}
    #     return {i: x for i, x in enumerate(obj.grnlist)}

    # def get_grnlist_as_dict(self, obj):
    #     print("object", obj.grnlist)
    #     if obj.grnlist is None:
    #         return {}
    #     return {i: x for i, x in enumerate(obj.grnlist)} or obj.process_store_Batch

class BatchMixSerializer(serializers.ModelSerializer):
    # ingredients = BatchMixIngredientsSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    total_ingredient_cost=serializers.SerializerMethodField()
    cost_per_kg_template=serializers.SerializerMethodField()


    def get_total_ingredient_cost(self, obj):
        return round((obj.total_ingredient_cost),2)

    # def get_cost_per_kg_template(self, obj):
    #     # print(obj.total_ingredient_cost,'------------cost_per_ke_template')
    #     template_cost_per_kg=round((obj.total_ingredient_cost/obj.totalVolume),2)
    #     return template_cost_per_kg

    def get_cost_per_kg_template(self, obj):
        try:
            # Ensure totalVolume is valid and not zero
            if obj.totalVolume and obj.totalVolume > 0:
                template_cost_per_kg = round((obj.total_ingredient_cost / obj.totalVolume), 2)
            else:
                template_cost_per_kg = 0.00  # or some default value to represent invalid cost

            return template_cost_per_kg
        except (ZeroDivisionError, TypeError) as e:
            # Handle specific errors if needed, like logging
            print(f"Error calculating cost per kg: {e}")
            return 0.00  # or handle it as you see fit

    class Meta:
        model = BatchMix
        fields = ['id', 'batchName', 'batchCode', 'expDate',
                  'subCategory', 'is_deleted',
                  'batchDate', 'totalVolume',
                  'created', 'updated',
                  'ingredients','cost_per_liter','total_ingredient_cost','cost_per_kg','cost_per_kg_template','is_expired',]

    def get_ingredients(self, obj):
        ingredients = BatchMixIngredients.objects.filter(SyrupBatchMix=obj)
        serializer = BatchMixIngredientsSerializer(ingredients, many=True)
        return serializer.data

    def create(self, validated_data):
        batch_products_data = self.context['request'].data.get('ingredients', [])
        # print(batch_products_data, "batch_products_data")
        # Create SyrupBatchMix instance

        syrup_batch_mix = BatchMix.objects.create(**validated_data)

        # Create associated SyrupBatchMixIngredients instances
        for ingredient_data in batch_products_data:
            # SyrupBatchMixIngredients.objects.create(SyrupBatchMix=syrup_batch_mix, **ingredient_data)
            ingredient_instance = Material.objects.get(pk=ingredient_data['ingredient'])
            BatchMixIngredients.objects.create(SyrupBatchMix=syrup_batch_mix, ingredient=ingredient_instance,
                                                    percentage=ingredient_data['percentage'],
                                                    quantity=ingredient_data['quantity'],
                                                    )

        return syrup_batch_mix
# </editor-fold>



# <editor-fold desc="batch mix create and ingredient ">
# class BatchMixCreateSerializer(serializers.ModelSerializer):
#     ingredients = BatchMixIngredientsSerializer(many=True, read_only=True, source="batch_mix_ingredients")
#
#     def validate(self, attrs):
#         ingredient_data = self.context['request'].data.get('ingredients', [])
#         for item in ingredient_data:
#             for batch_id in item['batchId']:
#                 try:
#                     process_store = ProcessStore.objects.get(batch_id=batch_id)
#                 except:
#                     return serializers.ValidationError({"message":"process in batch does not exist  ","status": status.HTTP_400_BAD_REQUEST})
#
#                 # Check if the batch is expired
#                 if process_store.is_expired():
#                     return serializers.ValidationError(
#                         {"message": "Batch is expired and cannot be processed", "status": status.HTTP_400_BAD_REQUEST})
#                 if process_store.is_expired():
#                     raise serializers.ValidationError({"message":"Cannot deduct quantity from an expired batch.","status": status.HTTP_400_BAD_REQUEST})
#                 if process_store.currentQuantity <= 0:
#                     raise serializers.ValidationError({"message":"Current quantity is zero or does not exist. Deduction cannot be performed.","status": status.HTTP_400_BAD_REQUEST})
#
#                 if item['quantity'] > process_store.currentQuantity:
#                     raise serializers.ValidationError({"message":"Deduction amount exceeds available current quantity.","status": status.HTTP_400_BAD_REQUEST})
#
#         return attrs
#
#     class Meta:
#         model = BatchMix
#         fields = '__all__'
#
#     def create(self, validated_data):
#         ingredient_data = self.context['request'].data.get('ingredients', [])
#         syrup_batch_mix = BatchMix.objects.create(**validated_data)
#
#         ingredient_ids = [item['ingredient'] for item in ingredient_data]
#         material_matches = Material.objects.filter(id__in=ingredient_ids)
#         process_store_matches = ProcessStore.objects.filter(id__in=ingredient_ids)
#
#         for item in ingredient_data:
#             ingredient_id = item['ingredient']
#             material_match = material_matches.filter(id=ingredient_id).first()
#             process_store_match = process_store_matches.filter(id=ingredient_id)
#
#             # Check if both material and process store matches are found
#             if not material_match and not process_store_match.exists():
#                 print(f"Skipping ingredient ID {ingredient_id}: Material match: {material_match}, ProcessStore match: {process_store_match.exists()}")
#                 continue  # Skip this ingredient if either match is missing
#
#             # Attempt to create the BatchMixIngredients instance
#             try:
#                 batch_mix_ingredient, created = BatchMixIngredients.objects.get_or_create(
#                     SyrupBatchMix=syrup_batch_mix,
#                     ingredient=material_match,
#                     percentage=item['percentage'],
#                     quantity=item['quantity']
#                 )
#                 print(batch_mix_ingredient, '=========ingredient created')
#
#                 # Set ingredient_process_store only if there are matches
#                 if process_store_match.exists():
#                     batch_mix_ingredient.ingredient_process_store.set(process_store_match)
#                 batch_mix_ingredient.save()
#                 for batch_id in item['batchId']:
#                     process_store = ProcessStore.objects.get(batch_id=batch_id)
#                     # Deduct quantity if batch is not expired
#                     process_store.deduct_quantity(item['quantity'])
#                     print("deduct from process store",item['quantity'])
#
#
#             except Exception as e:
#                 print(f"Error creating BatchMixIngredient: {str(e)}")
#                 # Rollback created BatchMix if an ingredient fails
#                 syrup_batch_mix.delete()  # Remove the created BatchMix
#                 raise serializers.ValidationError({"message":"Failed to create BatchMix and related ingredients."})
#
#         return validated_data

# <editor-fold desc="except icre">
class BatchMixCreateSerializer(serializers.ModelSerializer):
    ingredients=BatchMixIngredientsSerializer(many=True,read_only=True,source="batch_mix_ingredients")
    class Meta:
        model = BatchMix
        fields = '__all__'

    def create(self, validated_data):
        batch_data = self.context['batch']
        ingredient_data = self.context['request'].data.get('ingredients', [])

        print(batch_data,'===========data')

        try:
            with transaction.atomic():
                syrup_batch_mix = BatchMix.objects.create(**validated_data)

                ingredient_ids = [item['ingredient'] for item in ingredient_data]
                material_matches = Material.objects.filter(id__in=ingredient_ids)
                process_store_matches = ProcessStore.objects.filter(id__in=ingredient_ids)

                for item in ingredient_data:
                    print(item,'---------------items data')
                    ingredient_id = item['ingredient']

                    material_match = material_matches.filter(id=ingredient_id).first()
                    # if material_match:
                    print(f"Matched in Material: {material_match}")

                    process_store_match = process_store_matches.filter(id=ingredient_id)
                    # if process_store_match.exists():
                    print(f"Matched in ProcessStore: {process_store_match}")

                    batch_mix_ingredient,created = BatchMixIngredients.objects.get_or_create(
                        SyrupBatchMix=syrup_batch_mix,
                        ingredient=material_match,
                        percentage=item['percentage'],
                        quantity=item['quantity']
                    )
                    print(batch_mix_ingredient,'=========ingredient making')

                    batch_mix_ingredient.ingredient_process_store.set(process_store_match)
                    batch_mix_ingredient.save()

                return syrup_batch_mix

        except Exception as e:
            # If any exception occurs, the transaction will be rolled back
            print(f"Error occurred: {str(e)}")
            raise serializers.ValidationError("Failed to create BatchMix and related objects.")
# </editor-fold>
# </editor-fold>

# <editor-fold desc="get batch">


class GetBatchMixDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchMix
        fields = ['id', 'batchName', 'batchCode', 'expDate',
                  'subCategory', 'is_deleted',
                  'batchDate', 'totalVolume',
                  'created', 'updated']
# </editor-fold>


# <editor-fold desc="batch mix updated ">
from django.db import models

class BatchMixUpdateSerializer(serializers.ModelSerializer):
    ingredients_data = serializers.DictField(write_only=True)
    expDate=serializers.DateField(format="%m/%d/%Y")
    class Meta:
        model = BatchMix
        fields = '__all__'

    def validate(self, attrs):


        """
        Validate BatchMix update and track quantity changes
        """
        if self.instance and self.instance.expDate:
            if self.instance.expDate < timezone.now().date():
                raise ValidationError({"message": "Cannot process expired BatchMix"})

        return attrs
    #
    def update(self, instance, validated_data):
        """
        Update BatchMix and handle quantity changes
        """
        ingredients_data = self.context['ingredients_data']
        batch_data = self.context['batch']
        print(ingredients_data, '==============data ing')
        print(batch_data, '======batch_data========data ing',validated_data)

        # Update BatchMix fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


        ingredient_ids_list = [item['ingredient'] for item in ingredients_data]
        ingredient_qty_map = {item['ingredient']: item['quantity'] for item in ingredients_data}

        print(ingredient_ids_list, '============given ids')

        matched_ingredients = BatchMixIngredients.objects.filter(
            models.Q(ingredient__id__in=ingredient_ids_list) |
            models.Q(ingredient_process_store__id__in=ingredient_ids_list),
            is_deleted=False,
            SyrupBatchMix=self.instance,
        ).distinct()

        quantity_changes = []
        print(matched_ingredients,'===========ingredients')
        for old_ingredient in matched_ingredients:

            grn_number = old_ingredient.grnlist[0] if old_ingredient.grnlist else None
            if grn_number:
                print(grn_number,'============grn number')
                grn = GoodsReturnNote.objects.filter(GRNnumber=grn_number).first()
                if grn is None or grn.expDate < timezone.now().date():
                    raise ValidationError({"message": "Cannot process expired GRN"})

            ingredient_id = old_ingredient.ingredient.id  if old_ingredient.ingredient else old_ingredient.ingredient_process_store.all().first().id
            print(ingredient_id,'==============id',old_ingredient.quantity,'========quntity')
            old_qty = old_ingredient.quantity
            new_qty = ingredient_qty_map.get(ingredient_id, old_qty)
            difference = new_qty - old_qty
            print(difference,'=============diffenece',new_qty,"new quntity",old_qty,"old quntiuty")

            # print(ingredient.id,'====ingredient==========data')
            if difference != 0:
                change_info = {
                    'id': ingredient_id,
                    'ingredient_name': str(old_ingredient.ingredient),
                    'old_quantity': old_qty,
                    'new_quantity': new_qty,
                    'difference': abs(difference),
                    'action': 'increase' if difference > 0 else 'decrease',
                    'grn_number': grn_number
                }
                # print(change_info,'=============change data')

                quantity_changes.append(change_info)
        #
                print(f"\nIngredient id: {change_info['id']}")
                print(f"Ingredient: {change_info['ingredient_name']}")
                print(f"GRN Number: {change_info['grn_number']}")
                print(f"Current quantity: {old_qty}")
                print(f"New quantity: {new_qty}")

                # ==============================
                # if difference > 0:
                #     change_info['additional_needed'] = difference
                #     # Allocate from GRNs for increases
                #     grn_list = [{'GRNnumber': grn_number, 'quantity': old_qty}]  # Adjust based on actual GRN data
                #     updated_grn_list = self.allocate_from_grn(grn_list, difference)
                #
                # else:
                #     change_info['remaining'] = abs(difference)
                    # # Return to GRNs for decreases
                    # grn_list = [{'GRNnumber': grn_number, 'quantity': old_qty}]  # Adjust based on actual GRN data
                    # updated_grn_list = self.return_to_grn(grn_list, abs(difference))

                # ==============================

                if difference > 0:
                    print(f"Action: INCREASE - Need {difference} more units")
                    ingredient = BatchMixIngredients.objects.get(id=old_ingredient.id)
                    ingredient.quantity=new_qty
                    ingredient.save()
                    store_data = Store.objects.get(materialName__id=change_info['id'])

                    grn=StoreGRN.objects.get(store=store_data.id)
                    grn.totalQuantity-=validated_data.get('totalVolume')
                    grn.save()
                else:
                    print(f"Action: DECREASE - {abs(difference)} units will be remaining")
                    ingredient = BatchMixIngredients.objects.get(id=old_ingredient.id)
                    ingredient.quantity = new_qty
                    ingredient.save()
                    store_data=Store.objects.get(materialName__id=change_info['id'])
                    store_data.currentQuantity+=change_info['difference']
                    store_data.save()
                    grn=StoreGRN.objects.get(store=store_data.id)
                    grn.totalQuantity+=validated_data.get('totalVolume')
                    grn.save()


        matched_ingredient_ids = set(matched_ingredients.values_list('id', flat=True))
        print("Matched BatchMixIngredients IDs:===", list(matched_ingredient_ids))

        return validated_data

    # def return_to_grn(self, grn_list, quantity):
    #     print("return calling ")
    #
    #     updated_grn_list = []
    #     for grn_data in grn_list:
    #         if quantity <= 0:
    #             updated_grn_list.append(grn_data)
    #             continue
    #
    #         grn_obj = GoodsReturnNote.objects.filter(GRNnumber=grn_data['GRNnumber']).first()
    #         if grn_obj and not grn_obj.expDate < timezone.now().date():  # Check for expiration
    #             return_quantity = min(quantity, grn_data['quantity'])
    #             grn_obj.currentQuantity += return_quantity
    #             grn_obj.save()
    #             quantity -= return_quantity
    #
    #             if grn_data['quantity'] > return_quantity:
    #                 grn_data['quantity'] -= return_quantity
    #                 updated_grn_list.append(grn_data)
    #         else:
    #             updated_grn_list.append(grn_data)
    #     return updated_grn_list
    #
    # def allocate_from_grn(self,grn_list, quantity):
    #
    #     print("alowcated call ")
    #
    #     updated_grn_list = []
    #     for grn_data in grn_list:
    #         if quantity <= 0:
    #             updated_grn_list.append(grn_data)
    #             continue
    #
    #         grn_obj = GoodsReturnNote.objects.filter(GRNnumber=grn_data['GRNnumber']).first()
    #         if grn_obj and not grn_obj.expDate < timezone.now().date():  # Check for expiration
    #             allocate_quantity = min(quantity, grn_obj.currentQuantity)
    #             grn_obj.currentQuantity -= allocate_quantity
    #             grn_obj.save()
    #             quantity -= allocate_quantity
    #
    #             new_grn_data = grn_data.copy()
    #             new_grn_data['quantity'] = allocate_quantity
    #             updated_grn_list.append(new_grn_data)
    #         else:
    #             updated_grn_list.append(grn_data)
    #
    #     if quantity > 0:
    #         raise ValidationError({"message": f"Not enough quantity available in GRNs. Remaining required: {quantity}"})
    #     return updated_grn_list

# ============================================================================upated
                # ingredient = BatchMixIngredients.objects.get(id=old_ingredient.id)
                # ingredient.quantity = new_qty
                # ingredient.save()

                # if difference > 0:
                #     change_info['additional_needed'] = difference
                #     # Allocate from GRNs for increases
                #     grn_list = [{'GRNnumber': grn_number, 'quantity': old_qty}]  # Adjust based on actual GRN data
                #     updated_grn_list = self.allocate_from_grn(grn_list, difference)
                #
                # else:
                #     change_info['remaining'] = abs(difference)
                #     # Return to GRNs for decreases
                #     grn_list = [{'GRNnumber': grn_number, 'quantity': old_qty}]  # Adjust based on actual GRN data
                #     updated_grn_list = self.return_to_grn(grn_list, abs(difference))

# ============================================================================upated
# from django.utils import timezone
# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
# #
# class BatchMixIngredientUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BatchMixIngredients
#         fields = ['id', 'ingredient', 'percentage', 'quantity', 'grnlist', 'rate']
#
#
# class BatchMixUpdateSerializer(serializers.ModelSerializer):
#     ingredients = BatchMixIngredientUpdateSerializer(many=True, source='batch_mix_ingredients')
#
#     class Meta:
#         model = BatchMix
#         fields = '__all__'
#
#     def validate(self, attrs):
#         """
#         Validate BatchMix update and track quantity changes
#         """
#         # Check expiry date
#         # exp_date = attrs.get('expDate')
#         if self.instance.expDate and self.instance.expDate < timezone.now().date():
#             raise ValidationError({"message": "Cannot process expired BatchMix"})
#
#         # Store changes for use in update method
#         # self._quantity_changes = quantity_changes
#         return attrs
#
#     def update(self, instance, validated_data):
#         """
#         Update BatchMix and handle quantity changes
#         """
#         #
#         # ingredients_data = validated_data.get('ingredients', [])
#         # print(ingredients_data,'======gg')
#         quantity_changes = []
#         # for new_ingredient in ingredients_data:
#         #     try:
#         #
#         #         for old_ingredient in ingredients:
#         #
#         #             print(old_ingredient,'===========old_ingredient')
#         #
#         #             new_qty = float(new_ingredient.get('quantity', 0))
#         #             old_qty = float(old_ingredient.quantity)
#         #             difference = new_qty - old_qty
#         #
#         #             grn=GoodsReturnNote.objects.filter(GRNnumber=old_ingredient.grnlist[0]).first()
#         #             if grn is None and grn.expDate < timezone.now().date():
#         #                 return ValidationError({"message": "Cannot process expired GRN"})
#         #             if difference != 0:
#         #                 change_info = {
#         #                     'id': old_ingredient.id,
#         #                     'ingredient_name': str(old_ingredient.ingredient),
#         #                     'old_quantity': old_qty,
#         #                     'new_quantity': new_qty,
#         #                     'difference': abs(difference),  # Absolute difference
#         #                     'grn_data':grn,
#         #                     'action': 'increase' if difference > 0 else 'decrease'
#         #                 }
#         #
#         #                 # Add additional info for increases/decreases
#         #                 if difference > 0:
#         #                     change_info['additional_needed'] = difference
#         #                 else:
#         #                     change_info['remaining'] = abs(difference)
#         #
#         #                 quantity_changes.append(change_info)
#         #                 # # Print detailed change information
#         #                 # print(f"\nIngredient: {change_info['ingredient_name']}")
#         #                 # print(f"Current quantity: {old_qty}")
#         #                 # print(f"New quantity: {new_qty}")
#         #                 # print(f"GRN: {change_info['grn_data']}")
#         #                 #
#         #                 # if difference > 0:
#         #                 #     print(f"Action: INCREASE - Need {difference} more units")
#         #                 # else:
#                         #     print(f"Action: DECREASE - {abs(difference)} units will be remaining")
#
#             # except BatchMixIngredients.DoesNotExist:
#             #     raise ValidationError({
#             #         "message": f"Ingredient with ID {new_ingredient['id']} not found"
#             #     })
#             # print("=============================")
#             # print(quantity_changes[0])
#         print("=============================")
#
#
#         # try:
#         #     pass
#         #     # with transaction.atomic():
#         #     #     # Update BatchMix fields
#         #     #     for attr, value in validated_data.items():
#         #     #         if attr != 'batch_mix_ingredients':
#         #     #             setattr(instance, attr, value)
#         #     #     instance.save()
#         #     #
#         #     #     # Update ingredients
#         #     #     if 'batch_mix_ingredients' in validated_data:
#         #     #         for ingredient_data in validated_data['batch_mix_ingredients']:
#         #     #             ingredient = BatchMixIngredients.objects.get(
#         #     #                 id=ingredient_data['id'],
#         #     #                 SyrupBatchMix=instance
#         #     #             )
#         #     #
#         #     #             # Find the change record for this ingredient
#         #     #             change_record = next(
#         #     #                 (change for change in self._quantity_changes
#         #     #                  if change['id'] == ingredient_data['id']),
#         #     #                 None
#         #     #             )
#         #     #
#         #     #             if change_record:
#         #     #                 if change_record['action'] == 'increase':
#         #     #                     # Handle increase logic
#         #     #                     print(f"\nProcessing INCREASE for {change_record['ingredient_name']}:")
#         #     #                     print(f"Additional quantity needed: {change_record['additional_needed']}")
#         #     #                     # Add your logic here for handling increased quantity
#         #     #                     # For example: check inventory, allocate new stock, etc.
#         #     #
#         #     #                 else:  # decrease
#         #     #                     # Handle decrease logic
#         #     #                     print(f"\nProcessing DECREASE for {change_record['ingredient_name']}:")
#         #     #                     print(f"Quantity to reallocate: {change_record['remaining']}")
#         #     #                     # Add your logic here for handling decreased quantity
#         #     #                     # For example: return to inventory, create new batch, etc.
#         #     #
#         #     #             # Update ingredient fields
#         #     #             for key, value in ingredient_data.items():
#         #     #                 if key != 'id':
#         #     #                     setattr(ingredient, key, value)
#         #     #             ingredient.save()
#         #     #
#         #     #     return instance
#         #
#         # except Exception as e:
#         #     raise ValidationError({"message": f"Update failed: {str(e)}"})
#
#         return validated_data
# #
# class BatchMixIngredientUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BatchMixIngredients
#         fields = ['id', 'ingredient', 'percentage', 'quantity', 'grnlist', 'rate']
#
#
# class BatchMixUpdateSerializer(serializers.ModelSerializer):
#     ingredients = BatchMixIngredientUpdateSerializer(many=True, source='batch_mix_ingredients')
#
#     class Meta:
#         model = BatchMix
#         fields = '__all__'
#
#     def validate(self, attrs):
#         print(attrs, '===============attr')
#
#         exp_date = attrs.get('expDate')
#         if exp_date and exp_date < timezone.now().date():
#             raise ValidationError({"message": "Cannot process expired BatchMix"})
#
#         ingredients_data = attrs.get('batch_mix_ingredients', [])
#         for ingredient_data in ingredients_data:
#             print(ingredient_data,'===========data',self.instance)
#             # Get all ingredients related to this batch mix
#             ingredients_data = []
#             batch_ingredients = BatchMixIngredients.objects.filter(
#                 SyrupBatchMix=self.instance.id,
#                 is_deleted=False
#             )
#             # print(batch_ingredients, '============mix')
#             # Iterate through each ingredient and collect required data
#             for ingredient in batch_ingredients:
#                 ingredient_info = {
#                     'ingredient_name': ingredient.ingredient if ingredient.ingredient else 'Unknown',
#                     'quantity': ingredient.quantity if ingredient else 0,
#                     'grn_list': ingredient.grnlist[0]
#                 }
#                 instance_quantity=ingredient.quantity
#                 required_quantity = attrs.get('quantity', 0)
#
#                 if required_quantity <= instance_quantity :
#                     remaining_quantity = instance_quantity - required_quantity
#                     if remaining_quantity > 0:
#                         print(f"Remaining quantity: {remaining_quantity} will be allocated to a new ingredient,{instance_quantity}")
#
#
#                 additional_quantity_needed = required_quantity - instance_quantity
#                 print(additional_quantity_needed,'==========needed')
#
#                 ingredients_data.append(ingredient_info)
#             print(ingredients_data, '=============data here ')
#             main = {
#                 'batch_name': self.instance.batchName,
#                 'batch_code': self.instance.batchCode,
#                 'ingredients': ingredients_data
#             }
#             print(main, '==============do')
#
#         return attrs
#
#     def update(self, instance, validated_data):
#         # print(instance,'=======instance')
#         # print(validated_data,'==========data alid')
#         return instance



#
    # def validate_ingredient(self, ingredient_data):
    #     """
    #     Validate a single ingredient's data.
    #
    #     This method checks if there's enough quantity available for the ingredient,
    #     considering both the existing instance quantity and available GRN quantities.
    #
    #     Args:
    #         ingredient_data (dict): The ingredient data to be validated.
    #
    #     Raises:
    #         ValidationError: If there's not enough valid quantity available.
    #     """
    #     grn_list = ingredient_data.get('grnlist', [])
    #     required_quantity = ingredient_data.get('quantity', 0)
    #     print(grn_list,'===========grn list')
    #     print(required_quantity,'===========required quantity')
    #
    #
    #     instance_id = ingredient_data.get('id')
    #     instance_quantity = 0
    #     if instance_id:
    #         try:
    #             instance = BatchMixIngredients.objects.get(id=instance_id)
    #             instance_quantity = instance.quantity
    #             print(instance_quantity,'========batch mix ==instance quntity for ingredient')
    #         except BatchMixIngredients.DoesNotExist:
    #             pass
    #
    #     if required_quantity <= instance_quantity:
    #         remaining_quantity = instance_quantity - required_quantity
    #         if remaining_quantity > 0:
    #             print(f"Remaining quantity: {remaining_quantity} will be allocated to a new ingredient")
    #         return
    #
    #     additional_quantity_needed = required_quantity - instance_quantity

#         total_available = sum(
#             grn['quantity'] for grn in grn_list
#             if self.is_grn_valid(grn['GRNnumber'])
#         )
#         print(instance_quantity, '========instance quantity')
#         print(total_available, '=============total available')
#         print(additional_quantity_needed, '========additional quantity needed')
#         print(grn_list, '========here ', required_quantity, '========required quantity')
#
#
#         if total_available < additional_quantity_needed:
#             raise ValidationError({
#                 "message": f"Not enough valid quantity available. Additional Required: {additional_quantity_needed}, Available: {total_available}"
#             })
#
#         print("Validation passed. Quantity will be allocated in update or create methods.")
#
#     def is_grn_valid(self, grn_number):
#         """
#         Check if a GRN is valid (not expired and exists).
#
#         Args:
#             grn_number (str): The GRN number to check.
#
#         Returns:
#             bool: True if the GRN is valid, False otherwise.
#         """
#         try:
#             grn = GoodsReturnNote.objects.get(GRNnumber=grn_number)
#             return not grn.is_expired
#         except GoodsReturnNote.DoesNotExist:
#             return False
#
#     def update(self, instance, validated_data):
#         """
#         Update a BatchMix instance and its related ingredients.
#
#         This method updates the BatchMix fields, updates or creates ingredients,
#         handles remaining quantities, and updates the ProcessStore.
#
#         Args:
#             instance (BatchMix): The BatchMix instance to update.
#             validated_data (dict): The validated data to update with.
#
#         Returns:
#             BatchMix: The updated BatchMix instance.
#         """
#         ingredients_data = validated_data.pop('batch_mix_ingredients', [])
#
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         existing_ingredients = {ingredient.id: ingredient for ingredient in instance.batch_mix_ingredients.all()}
#         updated_ingredient_ids = []
#
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data.get('id')
#             if ingredient_id and ingredient_id in existing_ingredients:
#                 ingredient = existing_ingredients[ingredient_id]
#                 old_quantity = ingredient.quantity
#                 new_quantity = ingredient_data.get('quantity', 0)
#
#                 self.update_ingredient(ingredient, ingredient_data)
#                 updated_ingredient_ids.append(ingredient_id)
#
#                 if new_quantity < old_quantity:
#                     remaining_quantity = old_quantity - new_quantity
#                     new_ingredient_data = ingredient_data.copy()
#                     new_ingredient_data['quantity'] = remaining_quantity
#                     new_ingredient_data.pop('id', None)
#                     new_ingredient = self.create_ingredient(instance, new_ingredient_data)
#                     updated_ingredient_ids.append(new_ingredient.id)
#             else:
#                 new_ingredient = self.create_ingredient(instance, ingredient_data)
#                 updated_ingredient_ids.append(new_ingredient.id)
#
#         for ingredient_id, ingredient in existing_ingredients.items():
#             if ingredient_id not in updated_ingredient_ids:
#                 ingredient.delete()
#
#         self.update_process_store(instance)
#
#         return instance
#
#     def update_ingredient(self, ingredient, ingredient_data):
#         """
#         Update a single ingredient.
#
#         This method handles both increasing and decreasing quantities,
#         allocating from or returning to GRNs as needed.
#
#         Args:
#             ingredient (BatchMixIngredients): The ingredient instance to update.
#             ingredient_data (dict): The data to update the ingredient with.
#         """
#         required_quantity = ingredient_data.get('quantity', 0)
#         current_quantity = ingredient.quantity
#         grn_list = ingredient_data.get('grnlist', [])
#
#         if required_quantity <= current_quantity:
#             remaining = current_quantity - required_quantity
#             self.return_to_grn(grn_list, remaining)
# #         else:
# #             additional_needed = required_quantity - current_quantity
#             new_grn_list = self.allocate_from_grn(grn_list, additional_needed)
#             ingredient_data['grnlist'] = new_grn_list
#
#         for attr, value in ingredient_data.items():
#             setattr(ingredient, attr, value)
#         ingredient.save()
#
#     def create_ingredient(self, batch_mix, ingredient_data):
#         """
#         Create a new ingredient for a BatchMix.
#
#         This method allocates the required quantity from GRNs and creates a new ingredient.
#
#         Args:
#             batch_mix (BatchMix): The BatchMix instance to associate the new ingredient with.
#             ingredient_data (dict): The data for the new ingredient.
#
#         Returns:
#             BatchMixIngredients: The newly created ingredient instance.
#         """
#         required_quantity = ingredient_data.get('quantity', 0)
#         grn_list = ingredient_data.get('grnlist', [])
#         new_grn_list = self.allocate_from_grn(grn_list, required_quantity)
#         ingredient_data['grnlist'] = new_grn_list
#         return BatchMixIngredients.objects.create(SyrupBatchMix=batch_mix, **ingredient_data)
#
    # def return_to_grn(self, grn_list, quantity):
    #     """
    #     Return excess quantity back to GRNs.
    #
    #     This method updates GRN quantities and returns an updated GRN list.
    #
    #     Args:
    #         grn_list (list): List of GRN data.
    #         quantity (float): The quantity to return.
    #
    #     Returns:
    #         list: Updated GRN list.
    #     """
    #     updated_grn_list = []
    #     for grn_data in grn_list:
    #         if quantity <= 0:
    #             updated_grn_list.append(grn_data)
    #             continue
    #
    #         grn_obj = GoodsReturnNote.objects.filter(GRNnumber=grn_data['GRNnumber']).first()
    #         if grn_obj and not grn_obj.is_expired:
    #             return_quantity = min(quantity, grn_data['quantity'])
    #             grn_obj.approvedQuantity += return_quantity
    #             grn_obj.save()
    #             quantity -= return_quantity
    #
    #             if grn_data['quantity'] > return_quantity:
    #                 grn_data['quantity'] -= return_quantity
    #                 updated_grn_list.append(grn_data)
    #         else:
    #             updated_grn_list.append(grn_data)
    #
    #     return updated_grn_list
    #
    # def allocate_from_grn(self, grn_list, quantity):
    #     """
    #     Allocate quantity from GRNs.
    #
    #     This method allocates the required quantity from available GRNs and returns an updated GRN list.
    #
    #     Args:
    #         grn_list (list): List of GRN data.
    #         quantity (float): The quantity to allocate.
    #
    #     Returns:
    #         list: Updated GRN list.
    #
    #     Raises:
    #         ValidationError: If there's not enough quantity available in GRNs.
    #     """
    #     updated_grn_list = []
    #     for grn_data in grn_list:
    #         if quantity <= 0:
    #             updated_grn_list.append(grn_data)
    #             continue
    #
    #         grn_obj = GoodsReturnNote.objects.filter(GRNnumber=grn_data['GRNnumber']).first()
    #         if grn_obj and not grn_obj.is_expired:
    #             allocate_quantity = min(quantity, grn_obj.approvedQuantity)
    #             grn_obj.approvedQuantity -= allocate_quantity
    #             grn_obj.save()
    #             quantity -= allocate_quantity
    #
    #             new_grn_data = grn_data.copy()
    #             new_grn_data['quantity'] = allocate_quantity
    #             updated_grn_list.append(new_grn_data)
    #         else:
    #             updated_grn_list.append(grn_data)
    #
    #     if quantity > 0:
    #         raise ValidationError({"message": f"Not enough quantity available in GRNs. Remaining required: {quantity}"})
    #
    #     return updated_grn_list
#
#     def update_process_store(self, batch_mix):
#         """
#         Update or create the ProcessStore for a BatchMix.
#
#         This method updates the ProcessStore object associated with the BatchMix if it's not expired.
#
#         Args:
#             batch_mix (BatchMix): The BatchMix instance to update the ProcessStore for.
#         """
#         if not batch_mix.is_expired:
#             process_store, created = ProcessStore.objects.get_or_create(
#                 batch=batch_mix,
#                 defaults={
#                     'quantity': batch_mix.totalVolume,
#                     'expDate': batch_mix.expDate,
#                     'currentQuantity': batch_mix.totalVolume
#                 }
#             )
#             if not created:
#                 process_store.quantity = batch_mix.totalVolume
#                 process_store.expDate = batch_mix.expDate
#                 process_store.currentQuantity = batch_mix.totalVolume
#                 process_store.save()
# from django.db import models
# from django.utils import timezone
# from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
#
#
# class BatchMixIngredientUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BatchMixIngredients
#         fields = ['id', 'ingredient', 'percentage', 'quantity', 'grnlist', 'rate']
#
#
# class BatchMixUpdateSerializer(serializers.ModelSerializer):
#     ingredients = BatchMixIngredientUpdateSerializer(many=True, source='batch_mix_ingredients')
#
#     class Meta:
#         model = BatchMix
#         fields = '__all__'
#
#     def validate(self, attrs):
#         print(attrs, '===============attr')
#
#         # Check if BatchMix is expired
#         exp_date = attrs.get('expDate')
#         if exp_date and exp_date < timezone.now().date():
#             raise ValidationError({"message": "Cannot process expired BatchMix"})
#
#         ingredients_data = attrs.get('batch_mix_ingredients', [])
#         for ingredient_data in ingredients_data:
#             self.validate_ingredient(ingredient_data)
#
#         return attrs
#
#     def validate_ingredient(self, ingredient_data):
#         grn_list = ingredient_data.get('grnlist', [])
#         required_quantity = ingredient_data.get('quantity', 0)
#         print(grn_list,'========here ',required_quantity,'========required quntity')
#
#         # Calculate total available quantity from non-expired GRNs
#         total_available = sum(
#             grn['quantity'] for grn in grn_list
#             if self.is_grn_valid(grn['GRNnumber'])
#         )
#         print(total_available,'=============totak avalaiblle')
#         if total_available < required_quantity:
#             raise ValidationError({
#                 "message": f"Not enough valid quantity available. Required: {required_quantity}, Available: {total_available}"
#             })
#
#     def is_grn_valid(self, grn_number):
#         try:
#             grn = GoodsReturnNote.objects.get(GRNnumber=grn_number)
#             return not grn.is_expired
#         except GoodsReturnNote.DoesNotExist:
#             return False
#
#     def update(self, instance, validated_data):
#         ingredients_data = validated_data.pop('batch_mix_ingredients', [])
#
        # # Update BatchMix fields
        # for attr, value in validated_data.items():
        #     setattr(instance, attr, value)
        # instance.save()

#         # Update or create BatchMixIngredients
#         existing_ingredients = {ingredient.id: ingredient for ingredient in instance.batch_mix_ingredients.all()}
#         updated_ingredient_ids = []
#
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data.get('id')
#             if ingredient_id and ingredient_id in existing_ingredients:
#                 # Update existing ingredient
#                 self.update_ingredient(existing_ingredients[ingredient_id], ingredient_data)
#                 updated_ingredient_ids.append(ingredient_id)
#             else:
#                 # Create new ingredient
#                 new_ingredient = self.create_ingredient(instance, ingredient_data)
#                 updated_ingredient_ids.append(new_ingredient.id)
#
#         # Delete ingredients that are not in the update data
#         for ingredient_id, ingredient in existing_ingredients.items():
#             if ingredient_id not in updated_ingredient_ids:
#                 ingredient.delete()
#
#         # Update ProcessStore
#         self.update_process_store(instance)
#
#         return instance
#
#     def update_ingredient(self, ingredient, ingredient_data):
#         required_quantity = ingredient_data.get('quantity', 0)
#         current_quantity = ingredient.quantity
#         grn_list = ingredient_data.get('grnlist', [])
#
#         if required_quantity <= current_quantity:
#             # Case 1: Reducing quantity or keeping it the same
#             remaining = current_quantity - required_quantity
#             self.return_to_grn(grn_list, remaining)
#         else:
#             # Case 2: Increasing quantity
#             additional_needed = required_quantity - current_quantity
#             new_grn_list = self.allocate_from_grn(grn_list, additional_needed)
#             ingredient_data['grnlist'] = new_grn_list
#
#         for attr, value in ingredient_data.items():
#             setattr(ingredient, attr, value)
#         ingredient.save()
#
#     def create_ingredient(self, batch_mix, ingredient_data):
#         required_quantity = ingredient_data.get('quantity', 0)
#         grn_list = ingredient_data.get('grnlist', [])
#         new_grn_list = self.allocate_from_grn(grn_list, required_quantity)
#         ingredient_data['grnlist'] = new_grn_list
#         return BatchMixIngredients.objects.create(SyrupBatchMix=batch_mix, **ingredient_data)
#
#     def return_to_grn(self, grn_list, quantity):
#         updated_grn_list = []
#         for grn_data in grn_list:
#             if quantity <= 0:
#                 updated_grn_list.append(grn_data)
#                 continue
#
#             grn_obj = GoodsReturnNote.objects.filter(GRNnumber=grn_data['GRNnumber']).first()
#             if grn_obj and not grn_obj.is_expired:
#                 return_quantity = min(quantity, grn_data['quantity'])
#                 grn_obj.approvedQuantity += return_quantity
#                 grn_obj.save()
#                 quantity -= return_quantity
#
#                 if grn_data['quantity'] > return_quantity:
#                     grn_data['quantity'] -= return_quantity
#                     updated_grn_list.append(grn_data)
#             else:
#                 updated_grn_list.append(grn_data)
#
#         return updated_grn_list
#
#     def allocate_from_grn(self, grn_list, quantity):
#         updated_grn_list = []
#         for grn_data in grn_list:
#             if quantity <= 0:
#                 updated_grn_list.append(grn_data)
#                 continue
#
#             grn_obj = GoodsReturnNote.objects.filter(GRNnumber=grn_data['GRNnumber']).first()
#             if grn_obj and not grn_obj.is_expired:
#                 allocate_quantity = min(quantity, grn_obj.approvedQuantity)
#                 grn_obj.approvedQuantity -= allocate_quantity
#                 grn_obj.save()
#                 quantity -= allocate_quantity
#
#                 new_grn_data = grn_data.copy()
#                 new_grn_data['quantity'] = allocate_quantity
#                 updated_grn_list.append(new_grn_data)
#             else:
#                 updated_grn_list.append(grn_data)
#
#         if quantity > 0:
#             raise ValidationError({"message": f"Not enough quantity available in GRNs. Remaining required: {quantity}"})
#
#         return updated_grn_list
#
#     def update_process_store(self, batch_mix):
#         if not batch_mix.is_expired:
#             process_store, created = ProcessStore.objects.get_or_create(
#                 batch=batch_mix,
#                 defaults={
#                     'quantity': batch_mix.totalVolume,
#                     'expDate': batch_mix.expDate,
#                     'currentQuantity': batch_mix.totalVolume
#                 }
#             )
#             if not created:
#                 process_store.quantity = batch_mix.totalVolume
#                 process_store.expDate = batch_mix.expDate
#                 process_store.currentQuantity = batch_mix.totalVolume
#                 process_store.save()

# class BatchMixIngredientUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BatchMixIngredients
#         fields = ['id', 'ingredient', 'percentage', 'quantity', 'grnlist', 'rate']
#
# class BatchMixUpdateSerializer(serializers.ModelSerializer):
#     ingredients = BatchMixIngredientUpdateSerializer(many=True, source='batch_mix_ingredients')
#
#     def validate(self, attrs):
#         print(attrs,'===============attr')
#         return attrs
#
#     class Meta:
#         model = BatchMix
#         fields='__all__'
#         # fields = ['id', 'batchName', 'batchCode', 'batchDate', 'expDate', 'subCategory', 'totalVolume', 'ingredients','is_expired']
#
#     def update(self, instance, validated_data):
#         ingredients_data = validated_data.pop('batch_mix_ingredients', [])
#
#         # Update BatchMix fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         # Update or create BatchMixIngredients
#         existing_ingredients = {ingredient.id: ingredient for ingredient in instance.batch_mix_ingredients.all()}
#         ingredient_ids = []
#
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data.get('id')
#             if ingredient_id and ingredient_id in existing_ingredients:
#                 # Update existing ingredient
#                 self.update_ingredient(existing_ingredients[ingredient_id], ingredient_data)
#                 ingredient_ids.append(ingredient_id)
#             else:
#                 # Create new ingredient
#                 ingredient = BatchMixIngredients.objects.create(SyrupBatchMix=instance, **ingredient_data)
#                 ingredient_ids.append(ingredient.id)
#
#         # Delete ingredients that are not in the update data
#         for ingredient_id, ingredient in existing_ingredients.items():
#             if ingredient_id not in ingredient_ids:
#                 ingredient.delete()
#
#         # Update ProcessStore
#         self.update_process_store(instance)
#
#         return instance
#
#     def update_ingredient(self, ingredient, ingredient_data):
#         for attr, value in ingredient_data.items():
#             setattr(ingredient, attr, value)
#         ingredient.save()
#
#     def update_process_store(self, batch_mix):
#         try:
#             process_store = ProcessStore.objects.get(batch=batch_mix)
#             process_store.quantity = batch_mix.totalVolume
#             process_store.expDate = batch_mix.expDate
#             process_store.currentQuantity = batch_mix.totalVolume
#             process_store.save()
#         except ProcessStore.DoesNotExist:
#             ProcessStore.objects.create(
#                 batch=batch_mix,
#                 quantity=batch_mix.totalVolume,
#                 expDate=batch_mix.expDate,
#                 currentQuantity=batch_mix.totalVolume
#             )
#




# class BatchMixIngredientUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BatchMixIngredients
#         fields = ['id', 'ingredient', 'percentage', 'quantity', 'grnlist', 'rate']
#
#
# class BatchMixUpdateSerializer(serializers.ModelSerializer):
#     ingredients = BatchMixIngredientUpdateSerializer(many=True, source='batch_mix_ingredients')
#
#     def validate(self, attrs):
#         print(attrs,'===============attr')
#         return attrs
#
#     class Meta:
#         model = BatchMix
#         fields = ['id', 'batchName', 'batchCode', 'batchDate', 'expDate', 'subCategory', 'totalVolume', 'ingredients','is_expired']
#
#     def update(self, instance, validated_data):
#         ingredients_data = validated_data.pop('batch_mix_ingredients', [])
#
#         # Update BatchMix fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         # Update or create BatchMixIngredients
#         existing_ingredients = {ingredient.id: ingredient for ingredient in instance.batch_mix_ingredients.all()}
#         ingredient_ids = []
#
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data.get('id')
#             if ingredient_id and ingredient_id in existing_ingredients:
#                 # Update existing ingredient
#                 self.update_ingredient(existing_ingredients[ingredient_id], ingredient_data)
#                 ingredient_ids.append(ingredient_id)
#             # else:
#             #     # Create new ingredient
#             #     ingredient = BatchMixIngredients.objects.create(SyrupBatchMix=instance, **ingredient_data)
#             #     ingredient_ids.append(ingredient.id)
#
#         # Delete ingredients that are not in the update data
#         for ingredient_id, ingredient in existing_ingredients.items():
#             if ingredient_id not in ingredient_ids:
#                 ingredient.delete()
#
#         # Update ProcessStore
#         self.update_process_store(instance)
#
#         return instance
#
#     def update_ingredient(self, ingredient, ingredient_data):
#         for attr, value in ingredient_data.items():
#             setattr(ingredient, attr, value)
#         ingredient.save()
#
#     def update_process_store(self, batch_mix):
#         try:
#             process_store = ProcessStore.objects.get(batch=batch_mix)
#             process_store.quantity = batch_mix.totalVolume
#             process_store.expDate = batch_mix.expDate
#             process_store.currentQuantity = batch_mix.totalVolume
#             process_store.save()
#         except ProcessStore.DoesNotExist:
#             ProcessStore.objects.create(
#                 batch=batch_mix,
#                 quantity=batch_mix.totalVolume,
#                 expDate=batch_mix.expDate,
#                 currentQuantity=batch_mix.totalVolume
#             )
# </editor-fold>


# <editor-fold desc="exired check batch mix">
from datetime import date
from rest_framework import serializers

class BatchMixUpdateExpiredSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        # Get expiration date and is_expired flag from request or instance
        expDate = attrs.get('expDate', self.instance.expDate if self.instance else None)
        is_expired = attrs.get('is_expired', self.instance.is_expired if self.instance else False)

        # Handle expired date logic
        if expDate and expDate < date.today():
            if not is_expired:
                attrs['is_expired'] = True  # Set is_expired to True if expDate is expired
                self.handle_expired_deductions(self.instance)  # Apply deductions

        # Validate is_expired for future expiration dates
        elif expDate and expDate >= date.today() and is_expired:
            raise serializers.ValidationError({'message': 'batch is not expired ','status':status.HTTP_400_BAD_REQUEST})

        return attrs

    def handle_expired_deductions(self, instance):
        # Deduct current quantities from totalVolume based on expired ProcessStore entries
        for store in ProcessStore.objects.filter(batch=instance, expDate__lt=date.today()):
            instance.totalVolume -= store.currentQuantity  # Deduct currentQuantity from totalVolume
        instance.save()  # Save updated total volume

    class Meta:
        model = BatchMix
        fields = ['id', 'is_expired']
# </editor-fold>


# ===============================get ice cream related =========================

class BatchMixIceCreamTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchMixIceCreamTemplate
        fields = '__all__'  # or specify the fields you want to include

class BatchMixIcreamGetTemplateDetailsSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    total_ingredient_cost=serializers.SerializerMethodField()
    cost_per_kg_template=serializers.SerializerMethodField()

    def get_total_ingredient_cost(self, obj):
        return round((obj.total_ingredient_cost),2)

    def get_cost_per_kg_template(self, obj):
        try:
            # Ensure totalVolume is valid and not zero
            if obj.totalVolume and obj.totalVolume > 0:
                template_cost_per_kg = round((obj.total_ingredient_cost / obj.totalVolume), 2)
            else:
                template_cost_per_kg = 0.00  # or some default value to represent invalid cost

            return template_cost_per_kg
        except (ZeroDivisionError, TypeError) as e:
            # Handle specific errors if needed, like logging
            print(f"Error calculating cost per kg: {e}")
            return 0.00  # or handle it as you see fit

    class Meta:
        model=BatchMix
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Get the first template (assuming there's only one relevant template)
        template = BatchMixIceCreamTemplate.objects.filter(subCategory__category=instance.subCategory.category).first()

        if template:
            # Add template fields to the main representation
            template_fields = [
                'expDays', 'milk_fat_percentage', 'milk_snf_percentage',
                'batch_fat_percentage', 'batch_snf_percentage', 'cream_percentage',
                'butter_percentage', 'smp_snf_percentage', 'standard_converstion_factor'
            ]

            for field in template_fields:
                representation[field] = getattr(template, field)

        # Remove the 'templates' field if it exists
        representation.pop('templates', None)

        return representation
    def get_ingredients(self, obj):
        ingredients = BatchMixIngredients.objects.filter(SyrupBatchMix=obj)
        serializer = BatchMixIngredientsSerializer(ingredients, many=True)
        return serializer.data
    #


# choclate icecream create
# <editor-fold desc="except icre">
class BatchMixChocolateIceCreateSerializer(serializers.ModelSerializer):
    ingredients=BatchMixIngredientsSerializer(many=True,read_only=True,source="batch_mix_ingredients")
    class Meta:
        model = BatchMix
        fields = '__all__'

    def create(self, validated_data):
        ingredient_data = self.context['request'].data.get('ingredients', [])

        try:
            with transaction.atomic():
                syrup_batch_mix = BatchMix.objects.create(**validated_data)

                ingredient_ids = [item['ingredient'] for item in ingredient_data]
                material_matches = Material.objects.filter(id__in=ingredient_ids)
                process_store_matches = ProcessStore.objects.filter(id__in=ingredient_ids)

                for item in ingredient_data:
                    ingredient_id = item['ingredient']

                    material_match = material_matches.filter(id=ingredient_id).first()
                    # if material_match:
                    print(f"Matched in Material: {material_match}")

                    process_store_match = process_store_matches.filter(id=ingredient_id)
                    # if process_store_match.exists():
                    print(f"Matched in ProcessStore: {process_store_match}")

                    batch_mix_ingredient,created = BatchMixIngredients.objects.get_or_create(
                        SyrupBatchMix=syrup_batch_mix,
                        ingredient=material_match,
                        percentage=item['percentage'],
                        quantity=item['quantity']
                    )
                    print(batch_mix_ingredient,'=========ingredient making')

                    batch_mix_ingredient.ingredient_process_store.set(process_store_match)
                    batch_mix_ingredient.save()

                return syrup_batch_mix

        except Exception as e:
            # If any exception occurs, the transaction will be rolled back
            print(f"Error occurred: {str(e)}")
            raise serializers.ValidationError("Failed to create BatchMix and related objects.")
# </editor-fold>