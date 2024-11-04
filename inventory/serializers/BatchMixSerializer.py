# from rest_framework import serializers
# from inventory.models import Batch, BatchIngredients, BatchMixCategory, BatchMixSubCategory, BatchMixTemplate, \
#     BatchMixTemplateIngredients, Material
# from inventory.view import SyrupBatchMix
# from process_batch.serializers.batchMixTemplateForSyrupAndSauceSerializer import ProcessStoreSyrupAndSauceSerializer
# from process_store.models import ProcessStoreSyrupAndSauce
#
#
# class GETBatchIngredientsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BatchIngredients
#         fields = ['id', 'materialName', 'quantity', 'price', 'total', 'created', 'updated']
#         read_only_fields = ['id', 'created', 'updated']
#         depth = 1
#
#
# class BatchIngredientsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BatchIngredients
#         fields = ['id', 'materialName', 'quantity', 'price', 'total', 'created', 'updated']
#         read_only_fields = ['id', 'created', 'updated']
#         # depth = 1
#
#
# class BatchSerializer(serializers.ModelSerializer):
#     batch_ingredients = BatchIngredientsSerializer(many=True, write_only=True)
#
#     class Meta:
#         model = Batch
#         fields = ['id', 'batchName', 'batchCode', 'totalQuantity', 'totalAmount', 'batch_ingredients', 'created',
#                   'updated']
#         read_only_fields = ['id', 'created', 'updated']
#
#     def create(self, validated_data):
#         batch_ingredients_data = validated_data.pop('batch_ingredients')
#         batch = Batch.objects.create(**validated_data)
#         for ingredient_data in batch_ingredients_data:
#             BatchIngredients.objects.create(batch=batch, **ingredient_data)
#         return batch
#
#     def update(self, instance, validated_data):
#         batch_ingredients_data = validated_data.pop('batch_ingredients')
#
#         # Update the Batch instance
#         instance.batchName = validated_data.get('batchName', instance.batchName)
#         instance.batchCode = validated_data.get('batchCode', instance.batchCode)
#         instance.totalAmount = validated_data.get('totalAmount', instance.totalAmount)
#         instance.totalQuantity = validated_data.get('totalQuantity', instance.totalQuantity)
#         instance.save()
#
#         # Clear existing BatchIngredients
#         instance.batchingredients_set.all().delete()
#
#         # Add new BatchIngredients
#         for ingredient_data in batch_ingredients_data:
#             BatchIngredients.objects.create(batch=instance, **ingredient_data)
#
#         return instance
#
#
# # ---------------------------------------------------------------------------------------------------------
# #                                               New Serializers
# # ---------------------------------------------------------------------------------------------------------
#
#
# class BatchMixCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BatchMixCategory
#         fields = "__all__"
#
#
# class BatchMixSubCategorySerializer(serializers.ModelSerializer):
#     category_name = serializers.CharField(source='category.name', read_only=True)
#
#     class Meta:
#         model = BatchMixSubCategory
#         fields = "__all__"
#         # depth =1
#
#
# # POST Method for template
# # class MaterialSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Material
# #         fields = ['id', 'materialName', 'materialDescription', 'type']
# #
#
# # class BatchMixTemplateIngredientsSerializer(serializers.ModelSerializer):
# #     ingredient = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), required=False)
# #
# #
# #     class Meta:
# #         model = BatchMixTemplateIngredients
# #         fields = ['ingredient', 'percentage', 'lowerLimit', 'upperLimit', 'type']
# #         depth = 1
#
#
# class BatchMixTemplateIngredientsSerializer(serializers.ModelSerializer):
#     ingredient = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), required=False)
#
#     class Meta:
#         model = BatchMixTemplateIngredients
#         fields = ['ingredient', 'percentage', 'lowerLimit', 'upperLimit', 'type']
#         depth = 1
#
#     def __init__(self, *args, **kwargs):
#         # Initialize the parent serializer first
#         super().__init__(*args, **kwargs)
#
#         # Catch any potential issues during queryset assignment
#         try:
#             # Check if data or instance is passed
#             if self.instance:
#                 # If instance exists, check the type and adjust queryset
#                 if self.instance.type == 'ProcessStore':
#                     # ingredients_process_store = ProcessStoreSyrupAndSauce.objects.all()
#                     # ingredients_process_store_serialized_data = ProcessStoreSyrupAndSauceSerializer(ingredients_process_store)
#                     self.fields['ingredient'].queryset = ProcessStoreSyrupAndSauce.objects.all()
#                 else:
#                     self.fields['ingredient'].queryset = Material.objects.all()
#             elif self.context.get('request') and self.context['request'].data.get('type') == 'ProcessStore':
#                 # In case of creation, use the context (e.g., request data) to determine the type
#                 self.fields['ingredient'].queryset = SyrupBatchMix.objects.all()
#             else:
#                 self.fields['ingredient'].queryset = Material.objects.all()
#
#         except Exception as e:
#             print(f"Error in BatchMixTemplateIngredientsSerializer: {str(e)}")
#
#
# class BatchMixTemplateSerializer(serializers.ModelSerializer):
#     ingredients = BatchMixTemplateIngredientsSerializer(many=True, required=False)
#     # category_name = serializers.SerializerMethodField()
#     subCategory = serializers.PrimaryKeyRelatedField(queryset=BatchMixSubCategory.objects.all(), required=False)
#
#     class Meta:
#         model = BatchMixTemplate
#         # fields = ['batchName', 'batchCode', 'subCategory', 'ingredients', 'category_name']
#         fields = ['batchName', 'batchCode', 'subCategory', 'ingredients', 'expDays']
#         depth = 1
#
#     # def get_category_name(self, obj):
#     #     return obj.subCategory.category.name if obj.subCategory and obj.subCategory.category else None
#
#     # def get_subCategory(self, obj):
#     #     print(obj.subCategory, "obj.subCategory==========================================================")
#     #     return obj.subCategory.id if obj.subCategory else None
#
#     def create(self, validated_data):
#         try:
#             ingredients_data = validated_data.pop('ingredients', [])
#             # process_store = validated_data.pop('process_store', [])
#             batch_mix_template = BatchMixTemplate.objects.create(**validated_data)
#             print("===============================================================")
#             print(ingredients_data, "ingredients_data")
#             for ingredient_data in ingredients_data:
#                 BatchMixTemplateIngredients.objects.create(template=batch_mix_template, **ingredient_data)
#
#             return batch_mix_template
#         except Exception as e:
#             print(e)
#             raise serializers.ValidationError(e)
#
#
# # Get Method for template
# class MaterialSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Material
#         fields = ['id', 'materialName', 'materialDescription', 'type']
#
#
# class GetBatchMixTemplateIngredientsSerializer(serializers.ModelSerializer):
#     # ingredient = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all())
#     ingredient = MaterialSerializer()
#
#     class Meta:
#         model = BatchMixTemplateIngredients
#         fields = ['ingredient', 'percentage', 'lowerLimit', 'upperLimit']
#         depth = 1
#
#
# class GetBatchMixTemplateSerializer(serializers.ModelSerializer):
#     ingredients = GetBatchMixTemplateIngredientsSerializer(many=True, required=False)
#     category_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = BatchMixTemplate
#         fields = ['pk', 'batchName', 'batchCode', 'subCategory', 'ingredients', 'category_name', 'expDays']
#         depth = 1
#
#     def get_category_name(self, obj):
#         return obj.subCategory.category.name if obj.subCategory and obj.subCategory.category else None
