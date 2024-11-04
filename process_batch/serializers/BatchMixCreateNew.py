from rest_framework import serializers

from inventory.models import Material
from process_batch.models.BatchMix import BatchMixIngredients, BatchMix


# <editor-fold desc="create batch mix">
class BatchMixNewIngredientsSerializer(serializers.ModelSerializer):
    material_name = serializers.SerializerMethodField()
    grnlist_as_dict = serializers.SerializerMethodField()

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
        return obj.ingredient.materialName

    def get_grnlist_as_dict(self, obj):
        if not hasattr(obj, 'grnlist') or obj.grnlist is None or not obj.grnlist:
            return {i: x.batch.batchCode for i, x in enumerate(obj.ingredient_process_store.all())}

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

    # def get_grnlist_as_dict(self, obj):
    #     print("object", obj.grnlist)
    #     if obj.grnlist is None:
    #
    #         return {}
    #     return {i: x for i, x in enumerate(obj.grnlist)}
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

class BatchMixNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchMix
        fields = '__all__'


    def create(self, validated_data):

        print(validated_data,'-------------data')
        batch_products_data = self.context['request'].data.get('ingredients', [])
        print(batch_products_data, "---------------here my new api-----------------batch_products_data")
        # # Create SyrupBatchMix instance
        #
        syrup_batch_mix = BatchMix.objects.create(**validated_data)

        # Create associated SyrupBatchMixIngredients instances
        for ingredient_data in batch_products_data:
            ingredient_instance = Material.objects.get(pk=ingredient_data['ingredient'])

            batch_Ingredients=BatchMixIngredients.objects.create(SyrupBatchMix=syrup_batch_mix, ingredient=ingredient_instance,
                                                    percentage=ingredient_data['percentage'],
                                                    quantity=ingredient_data['quantity'],
                                                    )

        return validated_data
# </editor-fold>

# <editor-fold desc="new">
class BatchMixIngredientsNewSerializer(serializers.ModelSerializer):
    material_name = serializers.SerializerMethodField()
    grnlist_as_dict = serializers.SerializerMethodField()

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
        return obj.ingredient.materialName

    # def get_grnlist_as_dict(self, obj):
    #     print("object", obj.grnlist)
    #     if obj.grnlist is None:
    #
    #         return {}
    #     return {i: x for i, x in enumerate(obj.grnlist)}
    #
    #
    def get_grnlist_as_dict(self, obj):
        # Handle the case where grnlist is None
        if obj.grnlist is None:
            return {}

        # Handle the case where grnlist is an empty list
        if not obj.grnlist:
            return {i: x.batch.batchCode for i, x in enumerate(obj.ingredient_process_store.all())}
        # Create a dictionary from grnlist with index as key and item as value
        return {i: x for i, x in enumerate(obj.grnlist)}

class BatchMixNewDetailsSerializer(serializers.ModelSerializer):
    # ingredients = BatchMixIngredientsSerializer(many=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = BatchMix
        fields = ['id', 'batchName', 'batchCode', 'expDate',
                  'subCategory', 'is_deleted',
                  'batchDate', 'totalVolume',
                  'created', 'updated',
                  'ingredients']

    def get_ingredients(self, obj):
        ingredients = BatchMixIngredients.objects.filter(SyrupBatchMix=obj)
        serializer = BatchMixIngredientsNewSerializer(ingredients, many=True)
        return serializer.data

# </editor-fold>
