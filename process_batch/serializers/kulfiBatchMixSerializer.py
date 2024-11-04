from rest_framework import serializers

from inventory.models import Material
from process_batch.models.BatchMix import BatchMixIngredients, BatchMix
from process_batch.models.batchMixkulfyTemplate import BatchMixkulfyTemplateIngredients, BatchMixkulfyTemplate
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

    class Meta:
        model = BatchMixIngredients
        fields = '__all__'


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
class BatchMixIngredientsSerializer(serializers.ModelSerializer):
    material_name = serializers.SerializerMethodField()
    grnlist_as_dict = serializers.SerializerMethodField()
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

    # def get_grnlist_as_dict(self, obj):
    #     # Handle the case where grnlist is None
    #     if obj.grnlist is None:
    #         return {}
    #
    #     # Handle the case where grnlist is an empty list
    #     if not obj.grnlist:
    #         return {i: x.batch.batchCode for i, x in enumerate(obj.ingredient_process_store.all())}
    #     # Create a dictionary from grnlist with index as key and item as value
    #     return {i: x for i, x in enumerate(obj.grnlist)}
    def get_grnlist_as_dict(self, obj):
        if not hasattr(obj, 'grnlist') or obj.grnlist is None or not obj.grnlist:
            return {}

        if isinstance(obj.grnlist, list):
            # Get the first (and only) unique GRN
            unique_grn = next(iter(set(obj.grnlist)), None)
            return {0: unique_grn} if unique_grn else {}
        elif isinstance(obj.grnlist, str):
            # If grnlist is a string, split it and get the first unique GRN
            grnlist = [grn.strip() for grn in obj.grnlist.split(',') if grn.strip()]
            unique_grn = next(iter(set(grnlist)), None)
            return {0: unique_grn} if unique_grn else {}
        else:
            return {}

class BatchMixSerializer(serializers.ModelSerializer):
    # ingredients = BatchMixIngredientsSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    total_ingredient_cost=serializers.SerializerMethodField()
    cost_per_kg_template=serializers.SerializerMethodField()

    def get_total_ingredient_cost(self, obj):
        return round(obj.total_ingredient_cost,2)

    def get_cost_per_kg_template(self, obj):
        # print(obj.total_ingredient_cost,'------------cost_per_ke_template')
        template_cost_per_kg=round((obj.total_ingredient_cost/obj.totalVolume),2)
        return template_cost_per_kg

    class Meta:
        model = BatchMix
        fields = ['id', 'batchName', 'batchCode', 'expDate',
                  'subCategory', 'is_deleted',
                  'batchDate', 'totalVolume',
                  'created', 'updated',
                  'ingredients','cost_per_liter','total_ingredient_cost','cost_per_kg','cost_per_kg_template','is_expired',]

        # fields = ['id', 'batchName', 'batchCode', 'expDate',
        #           'subCategory', 'is_deleted',
        #           'batchDate', 'totalVolume',
        #           'created', 'updated',
        #           'ingredients','cost_per_liter','total_ingredient_cost','cost_per_kg','cost_per_kg_template']

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



class BatchMixCreateSerializer(serializers.ModelSerializer):
    ingredients=BatchMixIngredientsSerializer(many=True,read_only=True,source="batch_mix_ingredients")
    class Meta:
        model = BatchMix
        fields = '__all__'

    def create(self, validated_data):
        ingredient_data = self.context['request'].data.get('ingredients', [])
        syrup_batch_mix = BatchMix.objects.create(**validated_data)

        # print(batch_products_data,'--------------data')

        # Extract ingredient IDs from the data
        ingredient_ids = [item['ingredient'] for item in ingredient_data]

        # Query Material to find matching ingredients
        material_matches = Material.objects.filter(id__in=ingredient_ids)

        # Query ProcessStore to find matching process store ingredients
        process_store_matches = ProcessStore.objects.filter(id__in=ingredient_ids)

        # Iterate over the ingredient data
        for item in ingredient_data:
            ingredient_id = item['ingredient']

            # Check if the ingredient matches in Material
            material_match = material_matches.filter(id=ingredient_id).first()
            if material_match:
                print(f"Matched in Material: {material_match}")

            # Check if the ingredient matches in ProcessStore (ManyToMany)
            process_store_match = process_store_matches.filter(id=ingredient_id)
            if process_store_match.exists():
                print(f"Matched in ProcessStore: {process_store_match}")

            # Assuming you want to save this to BatchMixIngredients
            batch_mix_ingredient = BatchMixIngredients.objects.create(
                SyrupBatchMix=syrup_batch_mix,  # Pass your BatchMix instance here
                ingredient=material_match,  # Save matched Material instance
                percentage=item['percentage'],
                quantity=item['quantity']
            )

            # Add matching ProcessStore records to the ManyToManyField
            batch_mix_ingredient.ingredient_process_store.set(process_store_match)
            batch_mix_ingredient.save()

        # ingredient_instance = Material.objects.filter(id__in=batch_products_data.get('ingredient')).values()
        # print(ingredient_instance, '--process---------------instance')

        # ingredient_instance_base = ProcessStore.objects.filter(id=ingredient_data.get('ingredient')).first()
        # print(ingredient_instance_base, '--base---------------instance')
        # ingredient_instance_base=None

        # # # Create the BatchMixIngredients
        # bing=BatchMixIngredients.objects.create(
        #     SyrupBatchMix=syrup_batch_mix,
        #     percentage=ingredient_data['percentage'],
        #     quantity=ingredient_data['quantity'],
        #     ingredient=ingredient_instance if ingredient_instance is None else ingredient_instance,
        # #     ingredient_process_store=ingredient_instance_base,
        # )
        # if ingredient_instance_base is not None:
        #     bing.ingredient_process_store.add(ingredient_instance_base)
        return validated_data


# <editor-fold desc="get batch">


class GetBatchMixSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchMix
        fields = ['id', 'batchName', 'batchCode', 'expDate',
                  'subCategory', 'is_deleted',
                  'batchDate', 'totalVolume',
                  'created', 'updated']
# </editor-fold>

# ======================================update==================
from rest_framework import serializers


class BatchMixKulfiTemplateIngredientsUpdateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)

    class Meta:
        model = BatchMixkulfyTemplateIngredients
        fields = ['id', 'object_id', 'content_type', 'type', 'lowerLimit', 'percentage', 'upperLimit']

    def validate_content_type(self, value):
        if value not in ["RMStore", "ProcessStore"]:
            raise serializers.ValidationError(f"Invalid content type: {value}")
        return value


class BatchMixKulfiTemplateUpdateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixKulfiTemplateIngredientsUpdateSerializer(many=True)

    class Meta:
        model = BatchMixkulfyTemplate
        fields = ['id', 'batchName', 'batchCode', 'expDays', 'subCategory', 'ingredients']

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])

        # Update BatchMixTemplate fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
