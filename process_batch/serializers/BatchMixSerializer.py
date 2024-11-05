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
    ingredients = BatchMixIngredientsSerializer(many=True, read_only=True,
                                                source="batch_mix_ingredients")  # Note the use of `many=True` since it's a one-to-many relationship

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
    ingredient = serializers.SerializerMethodField()

    def get_ingredient(self, obj):
        # Check if the 'ingredient' (Material) exists
        if obj.ingredient:
            return obj.ingredient.id

        # If 'ingredient' does not exist, check if there are any 'ingredient_process_store' entries
        if obj.ingredient_process_store.exists():
            # Retrieve the IDs from the related ProcessStore objects
            process_store_ids = [store.id for store in obj.ingredient_process_store.all()]
            print(process_store_ids, '--------------id')
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
            material = obj.process_store_names

        return material or "Unknown Material"

    def get_grnlist_as_dict(self, obj):
        if not hasattr(obj, 'grnlist') or obj.grnlist is None or not obj.grnlist:
            return {i: x.batch.batchCode for i, x in enumerate(obj.ingredient_process_store.all())}

        if isinstance(obj.grnlist, list):
            # Ensure grnlist items are hashable (e.g., if they are dicts, convert to tuples)
            hashable_grnlist = []
            for grn in obj.grnlist:
                if isinstance(grn, dict):
                    print(grn, '=========here i need grn grnlist')
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
    total_ingredient_cost = serializers.SerializerMethodField()
    cost_per_kg_template = serializers.SerializerMethodField()

    def get_total_ingredient_cost(self, obj):
        return round((obj.total_ingredient_cost), 2)

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
                  'ingredients', 'cost_per_liter', 'total_ingredient_cost', 'cost_per_kg', 'cost_per_kg_template',
                  'is_expired', ]

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


# <editor-fold desc="except icre">
class BatchMixCreateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixIngredientsSerializer(many=True, read_only=True, source="batch_mix_ingredients")

    class Meta:
        model = BatchMix
        fields = '__all__'

    def create(self, validated_data):
        batch_data = self.context['batch']
        ingredient_data = self.context['request'].data.get('ingredients', [])

        print(batch_data, '===========data')

        try:
            with transaction.atomic():
                syrup_batch_mix = BatchMix.objects.create(**validated_data)

                ingredient_ids = [item['ingredient'] for item in ingredient_data]
                material_matches = Material.objects.filter(id__in=ingredient_ids)
                process_store_matches = ProcessStore.objects.filter(id__in=ingredient_ids)

                for item in ingredient_data:
                    print(item, '---------------items data')
                    ingredient_id = item['ingredient']
                    material_match = material_matches.filter(id=ingredient_id).first()
                    # if material_match:
                    print(f"Matched in Material: {material_match}")

                    process_store_match = process_store_matches.filter(id=ingredient_id)
                    # if process_store_match.exists():
                    print(f"Matched in ProcessStore: {process_store_match}")

                    batch_mix_ingredient, created = BatchMixIngredients.objects.get_or_create(
                        SyrupBatchMix=syrup_batch_mix,
                        ingredient=material_match,
                        percentage=item['percentage'],
                        quantity=item['quantity']
                    )
                    print(batch_mix_ingredient, '=========ingredient making')

                    batch_mix_ingredient.ingredient_process_store.set(process_store_match)
                    batch_mix_ingredient.save()

                return syrup_batch_mix

        except Exception as e:
            # If any exception occurs, the transaction will be rolled back
            print(f"Error occurred: {str(e)}")
            raise serializers.ValidationError("Failed to create BatchMix and related objects.")


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
    expDate = serializers.DateField(format="%m/%d/%Y")

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
        print(batch_data, '======batch_data========data ing', validated_data)

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
        print(matched_ingredients, '===========ingredients')
        for old_ingredient in matched_ingredients:

            grn_number = old_ingredient.grnlist[0] if old_ingredient.grnlist else None
            if grn_number:
                print(grn_number, '============grn number')
                grn = GoodsReturnNote.objects.filter(GRNnumber=grn_number).first()
                if grn is None or grn.expDate < timezone.now().date():
                    raise ValidationError({"message": "Cannot process expired GRN"})

            ingredient_id = old_ingredient.ingredient.id if old_ingredient.ingredient else old_ingredient.ingredient_process_store.all().first().id
            print(ingredient_id, '==============id', old_ingredient.quantity, '========quntity')
            old_qty = old_ingredient.quantity
            new_qty = ingredient_qty_map.get(ingredient_id, old_qty)
            difference = new_qty - old_qty
            print(difference, '=============diffenece', new_qty, "new quntity", old_qty, "old quntiuty")

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
                    ingredient.quantity = new_qty
                    ingredient.save()
                    try:

                        print("change_info['id']=====INCREASE=========id", change_info['id'])
                        store_data = Store.objects.get(materialName__id=change_info['id'])
                        print(store_data, '===============store data i need')

                        grn = StoreGRN.objects.get(store=store_data.id)
                        grn.grn.totalQuantity -= validated_data.get('totalVolume')
                        grn.save()

                    except Exception as e:
                        print(e, "===========grn store=")

                    try:
                        print(change_info['id'], '==INCREASE======process==========batch')
                        store_data = ProcessStore.objects.get(id=change_info['id'])
                        print(store_data, '=========process ======store data i need')
                        grn = StoreGRN.objects.get(store=store_data.id)
                        grn.grn.totalQuantity -= validated_data.get('totalVolume')
                        grn.save()
                    except Exception as e:
                        print(e, '=================proccess ')


                else:
                    print(f"Action: DECREASE - {abs(difference)} units will be remaining")
                    ingredient = BatchMixIngredients.objects.get(id=old_ingredient.id)
                    ingredient.quantity = new_qty
                    ingredient.save()
                    try:
                        store_data = Store.objects.get(materialName__id=change_info['id'])
                        print(store_data, '========= DECREASE======store data i need')
                        store_data.currentQuantity += change_info['difference']
                        store_data.save()
                        grn = StoreGRN.objects.get(store=store_data.id)
                        grn.totalQuantity += validated_data.get('totalVolume')
                        grn.save()

                    except Exception as e:
                        print(e, '==========grn strore')
                    try:
                        store_data = ProcessStore.objects.get(id=change_info['id'])
                        print(store_data, '====DECREASE=====process ======store data i need')
                        store_data.currentQuantity += change_info['difference']
                        store_data.save()
                        grn = StoreGRN.objects.get(store=store_data.id)
                        grn.totalQuantity += validated_data.get('totalVolume')
                        grn.save()

                    except Exception as e:
                        print(e, '------process')

        return validated_data


# ============================================================================upated

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
            raise serializers.ValidationError(
                {'message': 'batch is not expired ', 'status': status.HTTP_400_BAD_REQUEST})

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
    total_ingredient_cost = serializers.SerializerMethodField()
    cost_per_kg_template = serializers.SerializerMethodField()

    def get_total_ingredient_cost(self, obj):
        return round((obj.total_ingredient_cost), 2)

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
    ingredients = BatchMixIngredientsSerializer(many=True, read_only=True, source="batch_mix_ingredients")

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

                    batch_mix_ingredient, created = BatchMixIngredients.objects.get_or_create(
                        SyrupBatchMix=syrup_batch_mix,
                        ingredient=material_match,
                        percentage=item['percentage'],
                        quantity=item['quantity']
                    )
                    print(batch_mix_ingredient, '=========ingredient making')

                    batch_mix_ingredient.ingredient_process_store.set(process_store_match)
                    batch_mix_ingredient.save()

                return syrup_batch_mix

        except Exception as e:
            # If any exception occurs, the transaction will be rolled back
            print(f"Error occurred: {str(e)}")
            raise serializers.ValidationError("Failed to create BatchMix and related objects.")


# </editor-fold>


# =============choclate ice cream cream create===============

# <editor-fold desc="batch mix chocolate icecream create ">

from rest_framework import serializers, status


class BatchMixChocolateIceCreameWithBaseBatchIdCreateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixIngredientsSerializer(many=True, read_only=True, source="batch_mix_ingredients")

    def validate(self, attrs):
        ingredient_data = self.context['request'].data.get('ingredients', [])
        print(ingredient_data)
        for item in ingredient_data:
            for batch_id in item['batchId']:
                print(batch_id, '====================bathc id')
                try:
                    batch = BatchMix.objects.filter(id=batch_id).first()
                    process_store = ProcessStore.objects.get(batch=batch)
                    # Check if the batch is expired
                    if process_store.is_expired():
                        raise serializers.ValidationError("Batch is expired and cannot be processed.",
                                                          code=status.HTTP_400_BAD_REQUEST)

                    # Check if the current quantity is zero or insufficient
                    if process_store.currentQuantity <= 0:
                        raise serializers.ValidationError(
                            "Current quantity is zero or does not exist. Deduction cannot be performed.",
                            code=status.HTTP_400_BAD_REQUEST)

                    if item['quantity'] > process_store.currentQuantity:
                        raise serializers.ValidationError("Deduction amount exceeds available current quantity.",
                                                          code=status.HTTP_400_BAD_REQUEST)

                except ProcessStore.DoesNotExist:
                    pass

        #
        return attrs

    class Meta:
        model = BatchMix
        fields = '__all__'

    def create(self, validated_data):
        batch_data = self.context['batch']
        ingredient_data = self.context['request'].data.get('ingredients', [])
        print(ingredient_data, '=============data ingredient making')

        with transaction.atomic():
            try:
                # Create the BatchMix instance
                syrup_batch_mix = BatchMix.objects.create(**validated_data)
                if not syrup_batch_mix:
                    raise serializers.ValidationError("BatchMix instance could not be created.")

                for item in ingredient_data:
                    ingredient_id = item['ingredient']
                    quantity = item['quantity']
                    percentage = item['percentage']
                    batch_ids = item.get('batchId', [])  # Assuming `batchId` is a list in each item

                    # Check if the ingredient_id exists in Material
                    material = Material.objects.filter(id=ingredient_id).first()
                    if material:
                        # Create BatchMixIngredients with Material
                        ingredients = BatchMixIngredients.objects.create(
                            SyrupBatchMix=syrup_batch_mix,
                            ingredient=material,
                            percentage=percentage,
                            quantity=quantity
                        )
                        print(f"Created BatchMixIngredients with Material ID: {ingredient_id}")
                    else:
                        # Check if the ingredient_id exists in ProcessStore
                        process_material = ProcessStore.objects.filter(id=ingredient_id).first()
                        if process_material:
                            # Create BatchMixIngredients with ProcessStore association
                            ingredient_process, created = BatchMixIngredients.objects.get_or_create(
                                SyrupBatchMix=syrup_batch_mix,
                                percentage=percentage,
                                quantity=quantity
                            )
                            if created:
                                ingredient_process.ingredient_process_store.set([process_material])
                                ingredient_process.save()
                                print(f"Created BatchMixIngredients with ProcessStore ID: {ingredient_id}")
                        else:
                            # If neither Material nor ProcessStore found, raise an error
                            raise serializers.ValidationError(
                                f"Ingredient ID {ingredient_id} does not match any Material or ProcessStore records."
                            )

                    # Deduct quantity from ProcessStores associated with batch IDs
                    process_stores = ProcessStore.objects.filter(batch_id__in=batch_ids)
                    for process_store in process_stores:
                        if process_store.currentQuantity < quantity:
                            raise serializers.ValidationError(
                                f"Insufficient quantity in ProcessStore for batch ID {process_store.batch_id}."
                            )
                        process_store.currentQuantity -= quantity
                        process_store.save()
                        print(
                            f"Updated ProcessStore with Batch ID {process_store.batch_id}, new quantity: {process_store.currentQuantity}")

            except Exception as e:
                print(f"Error occurred: {str(e)}")
                raise serializers.ValidationError(f"An error occurred: {str(e)}")

        return validated_data

    # def create(self, validated_data):
    #     batch_data = self.context['batch']
    #     ingredient_data = self.context['request'].data.get('ingredients', [])
    #     print(ingredient_data,'=============data ingredient making')
    #     with transaction.atomic():
    #         try:
    #             syrup_batch_mix = BatchMix.objects.create(**validated_data)
    #             if syrup_batch_mix:
    #
    #                 for item in ingredient_data:
    #
    #
    #                     try:
    #                         material = Material.objects.filter(id=item['ingredient']).first()
    #                         ingredients = BatchMixIngredients.objects.create(
    #                             SyrupBatchMix=batch_data,
    #                             ingredient=material,
    #                             percentage=item['percentage'],
    #                             quantity=item['quantity']
    #                         )
    #                     except Exception as e:
    #                         # print(e)
    #                         pass
    #
    #                     try:
    #                         proces_matrail = ProcessStore.objects.filter(id=item['ingredient']).first()
    #                         ingredient_process,created = BatchMixIngredients.objects.get_or_create(
    #                             SyrupBatchMix=batch_data,
    #                             percentage=item['percentage'],
    #                             quantity=item['quantity']
    #                         )
    #                         if created:
    #                             ingredient_process.ingredient_process_store.set(proces_matrail)
    #                             ingredient_process.save()
    #                     except Exception as e:
    #                         # print(e)
    #                         pass
    #
    #                     # Assuming item['batchId'] is a list of batch IDs
    #                     batch_ids = item['batchId']  # replace with the actual batch ID list from your item
    #                     process_stores = ProcessStore.objects.filter(batch_id__in=batch_ids)
    #
    #                     for process_store in process_stores:
    #                         process_store.currentQuantity-=item['quantity']
    #                         process_store.save()
    #                         # batch_mix_ingredients = BatchMixIngredients.objects.filter(SyrupBatchMix=process_store.batch,is_deleted=False)
    #                         #
    #                         # for ingredient in batch_mix_ingredients:
    #                         #     # Calculate the new quantity based on your logic (e.g., reduce by 10% or a fixed amount)
    #                         #     new_quantity = ingredient.quantity - item['quantity']  # example of a 10% decrease
    #                         #     percentage = ingredient.percentage - item['percentage']  # example of a 10% decrease
    #                         #     # Ensure quantity does not go below zero
    #                         #     ingredient.quantity = max(new_quantity, 0)
    #                         #     ingredient.save()
    #         except Exception as e:
    #             print(f"Error occurred: {str(e)}")
    #
    #     return validated_data
# </editor-fold>



class BatchMixChocolateIceCreamUpdateSerializer(serializers.ModelSerializer):
    ingredients_data = serializers.DictField(write_only=True)
    expDate = serializers.DateField(format="%m/%d/%Y")

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
        print(batch_data, '======batch_data========data ing', validated_data)


        for ingredient_instance in ingredients_data:
            items_batch_data=ingredient_instance['batchId']
            quantity = ingredient_instance['quantity']
            process_store_data=ProcessStore.objects.get(batch_id__in=items_batch_data)
            for process_store in process_store_data:
                if process_store.currentQuantity < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient quantity in ProcessStore for batch ID {process_store.batch_id}."
                    )
                process_store.currentQuantity -= quantity
                process_store.save()
                print(f"Updated ProcessStore with Batch ID {process_store.batch_id}, new quantity: {process_store.currentQuantity}")

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
        print(matched_ingredients, '===========ingredients')
        for old_ingredient in matched_ingredients:

            grn_number = old_ingredient.grnlist[0] if old_ingredient.grnlist else None
            if grn_number:
                print(grn_number, '============grn number')
                grn = GoodsReturnNote.objects.filter(GRNnumber=grn_number).first()
                if grn is None or grn.expDate < timezone.now().date():
                    raise ValidationError({"message": "Cannot process expired GRN"})

            ingredient_id = old_ingredient.ingredient.id if old_ingredient.ingredient else old_ingredient.ingredient_process_store.all().first().id
            print(ingredient_id, '==============id', old_ingredient.quantity, '========quntity')
            old_qty = old_ingredient.quantity
            new_qty = ingredient_qty_map.get(ingredient_id, old_qty)
            difference = new_qty - old_qty
            print(difference, '=============diffenece', new_qty, "new quntity", old_qty, "old quntiuty")

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
                    ingredient.quantity = new_qty
                    ingredient.save()
                    try:

                        print("change_info['id']=====INCREASE=========id", change_info['id'])
                        store_data = Store.objects.get(materialName__id=change_info['id'])
                        print(store_data, '===============store data i need')

                        grn = StoreGRN.objects.get(store=store_data.id)
                        grn.grn.totalQuantity -= validated_data.get('totalVolume')
                        grn.save()

                    except Exception as e:
                        print(e, "===========grn store=")

                    try:
                        print(change_info['id'], '==INCREASE======process==========batch')
                        store_data = ProcessStore.objects.get(id=change_info['id'])
                        print(store_data, '=========process ======store data i need')
                        grn = StoreGRN.objects.get(store=store_data.id)
                        grn.grn.totalQuantity -= validated_data.get('totalVolume')
                        grn.save()
                    except Exception as e:
                        print(e, '=================proccess ')


                else:
                    print(f"Action: DECREASE - {abs(difference)} units will be remaining")
                    ingredient = BatchMixIngredients.objects.get(id=old_ingredient.id)
                    ingredient.quantity = new_qty
                    ingredient.save()
                    try:
                        store_data = Store.objects.get(materialName__id=change_info['id'])
                        print(store_data, '========= DECREASE======store data i need')
                        store_data.currentQuantity += change_info['difference']
                        store_data.save()
                        grn = StoreGRN.objects.get(store=store_data.id)
                        grn.totalQuantity += validated_data.get('totalVolume')
                        grn.save()

                    except Exception as e:
                        print(e, '==========grn strore')
                    try:
                        store_data = ProcessStore.objects.get(id=change_info['id'])
                        print(store_data, '====DECREASE=====process ======store data i need')
                        store_data.currentQuantity += change_info['difference']
                        store_data.save()
                        grn = StoreGRN.objects.get(store=store_data.id)
                        grn.totalQuantity += validated_data.get('totalVolume')
                        grn.save()

                    except Exception as e:
                        print(e, '------process')

        return validated_data

