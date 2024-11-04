# from datetime import datetime
#
# from rest_framework import serializers
# from inventory.models import SyrupBatchMix, SyrupBatchMixIngredients, Material
#
#
# class SyrupBatchMixIngredientsSerializer(serializers.ModelSerializer):
#     material_name = serializers.SerializerMethodField()
#     grnlist_as_dict = serializers.SerializerMethodField()
#
#     class Meta:
#         model = SyrupBatchMixIngredients
#         fields = ['ingredient',
#                   'percentage',
#                   'quantity',
#                   'rate',
#                   'is_deleted',
#                   'created',
#                   'updated',
#                   'material_name',
#                   # 'grnlist',
#                   'grnlist_as_dict']
#
#     def get_material_name(self, obj):
#         return obj.ingredient.materialName
#
#     def get_grnlist_as_dict(self, obj):
#         if obj.grnlist is None:
#             return {}
#         return {i: x for i, x in enumerate(obj.grnlist)}
#
#
# class SyrupBatchMixSerializer(serializers.ModelSerializer):
#     # ingredients = SyrupBatchMixIngredientsSerializer(many=True)
#     ingredients = serializers.SerializerMethodField()
#
#     class Meta:
#         model = SyrupBatchMix
#         fields = ['id', 'batchName', 'batchCode', 'expDate',
#                   'subCategory', 'is_deleted',
#                   'batchDate', 'totalVolume',
#                   'created', 'updated',
#                   'ingredients']
#
#     def get_ingredients(self, obj):
#         ingredients = SyrupBatchMixIngredients.objects.filter(SyrupBatchMix=obj)
#         serializer = SyrupBatchMixIngredientsSerializer(ingredients, many=True)
#         return serializer.data
#
#     def create(self, validated_data):
#         batch_products_data = self.context['request'].data.get('ingredients', [])
#
#         # Create SyrupBatchMix instance
#         syrup_batch_mix = SyrupBatchMix.objects.create(**validated_data)
#
#         # Create associated SyrupBatchMixIngredients instances
#         for ingredient_data in batch_products_data:
#             # SyrupBatchMixIngredients.objects.create(SyrupBatchMix=syrup_batch_mix, **ingredient_data)
#             ingredient_instance = Material.objects.get(pk=ingredient_data['ingredient'])
#             SyrupBatchMixIngredients.objects.create(SyrupBatchMix=syrup_batch_mix, ingredient=ingredient_instance,
#                                                     percentage=ingredient_data['percentage'],
#                                                     quantity=ingredient_data['quantity'],
#                                                     )
#
#         return syrup_batch_mix
#
#
# class GetSyrupBatchMixSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SyrupBatchMix
#         fields = ['id', 'batchName', 'batchCode', 'expDate',
#                   'subCategory', 'is_deleted',
#                   'batchDate', 'totalVolume',
#                   'created', 'updated']
