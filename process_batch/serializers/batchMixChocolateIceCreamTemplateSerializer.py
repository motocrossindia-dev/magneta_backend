from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from inventory.models import Material
from process_batch.models.BatchMix import BatchMix
from process_batch.models.batchMixChocolateIceCreamTemplate import BatchMixChocolateIceCreamTemplateIngredients, \
    BatchMixChocolateIceCreamTemplate
from process_batch.models.categories import BatchMixSubCategory
from process_store.models import ProcessStore


class BatchMixChocolateIceCreamTemplateIngredientsSerializer(serializers.ModelSerializer):
    type = serializers.CharField()  # Model type passed from frontend
    ingredient_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BatchMixChocolateIceCreamTemplateIngredients
        # fields = "__all__"
        exclude = ['template']

    def validate(self, data):
        print(data, "incoming data to validate() in ingredient serializer")
        return data

    def create(self, validated_data):
        content_type = validated_data.pop('content_type')
        ingredient_id = validated_data.pop('ingredient_id')

        # Get the correct ContentType (Material or ProcessStoreSyrupAndSauce)
        if content_type == "RMStore":
            content_type = ContentType.objects.get_for_model(Material)
            print(content_type, "content_type")
        elif content_type == "processStore":
            content_type = ContentType.objects.get_for_model(ProcessStore)
            print(content_type, "content_type")
        else:
            raise serializers.ValidationError("Invalid ingredient type")

        # Create the ingredient record with the GenericForeignKey
        ingredient = BatchMixChocolateIceCreamTemplateIngredients.objects.create(
            content_type=content_type.pk,
            object_id=ingredient_id,
            **validated_data
        )

        return ingredient


class BatchMixChocolateIceCreamTemplateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixChocolateIceCreamTemplateIngredientsSerializer(many=True)
    subCategory = serializers.PrimaryKeyRelatedField(queryset=BatchMixSubCategory.objects.all(), required=False)

    class Meta:
        model = BatchMixChocolateIceCreamTemplate
        # fields = ['batchName', 'batchCode', 'subCategory', 'ingredients', 'expDays']
        fields = '__all__'
        depth = 1

    def validate(self, data):
        # Print data to inspect before validation
        print(data, "incoming data to validate()")
        return data

    def create(self, validated_data):
        print(validated_data,'--------------------data')
        # Extract the list of ingredients from the validated data
        ingredients_data = validated_data.pop('ingredients',[])

        # Create the BatchMixChocolateIceCreamTemplateForSyrupAndSauce instance
        batch_template = BatchMixChocolateIceCreamTemplate.objects.create(**validated_data)

        # Create each ingredient entry and associate it with the batch_template
        for ingredient_data in ingredients_data:
            ingredient_type = ingredient_data.pop('content_type')
            ingredient_id = ingredient_data.pop('ingredient_id')

            # Create the ingredient with the correct content_type and object_id
            BatchMixChocolateIceCreamTemplateIngredients.objects.create(
                template=batch_template,
                content_type=ingredient_type,
                # object_id=ingredient_id,
                **ingredient_data
            )
        return batch_template


# ==========================================================================================
class ProcessStoreSerializer(serializers.ModelSerializer):
    materialName = serializers.SerializerMethodField()
    materialDescription = serializers.SerializerMethodField()

    class Meta:
        model = ProcessStore
        fields = ['id', 'batch', 'quantity', 'expDate', 'currentQuantity', 'materialName', 'materialDescription']
        # depth = 1

    def get_materialName(self, obj):
        return obj.batch.batchName

    def get_materialDescription(self, obj):
        materialDescription = f"Exp Date: {obj.expDate}\nCurrent Quantity: {obj.currentQuantity}"
        return materialDescription


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'materialName', 'materialDescription', 'type']


# ======================
class contenttypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'
# ======================

class BatchMixNewDetailsSerializer(serializers.ModelSerializer):
    # # ingredients = BatchMixIngredientsSerializer(many=True)
    # ingredients = serializers.SerializerMethodField()

    class Meta:
        model = BatchMix
        fields='__all__'
    #     fields = ['id', 'batchName', 'batchCode', 'expDate',
    #               'subCategory', 'is_deleted',
    #               'batchDate', 'totalVolume',
    #               'created', 'updated',
    #               'ingredients']
    #
    # def get_ingredients(self, obj):
    #     ingredients = BatchMixIngredients.objects.filter(SyrupBatchMix=obj)
    #     serializer = BatchMixIngredientsNewSerializer(ingredients, many=True)
    #     return serializer.data


# ==================

# Serializer for the BatchMixChocolateIceCreamTemplateIngredientsForSyrupAndSauce model
class GETBatchMixChocolateIceCreamTemplateIngredientsSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()

    class Meta:
        model = BatchMixChocolateIceCreamTemplateIngredients
        fields ="__all__"
        # fields = ['type', 'lowerLimit', 'percentage', 'upperLimit', 'ingredient']
        depth = 3

    def get_ingredient(self, obj):
        print(obj,'=========data template')
        SERIALIZER_MAP = {
            'material': MaterialSerializer,
            'processstore': ProcessStoreSerializer,
        }
        if obj.content_type and obj.object_id:
            content_model = obj.content_type.model
            serializer_class = SERIALIZER_MAP.get(content_model)
            if serializer_class:
                # Serialize ingredient data
                data = serializer_class(obj.ingredient).data

                # Extract the `batch_name` from the current object
                batch_material = data.get('materialName',None)


                # print(batch_material, '------------batch name')

                # Ensure `batch_name` is not None or empty
                if batch_material:
                    # Check if the batch_name exists in multiple `BatchMix` entries
                    batch_instances = BatchMix.objects.filter(batchName=batch_material)  # Query for multiple matches

                    if batch_instances.exists():
                        # Serialize the full batch data for multiple instances
                        batch_data = BatchMixNewDetailsSerializer(batch_instances, many=True).data
                        # print(batch_data, '-------Batch data')

                        # Include batch data in the ingredient response
                        data['batch'] = batch_data  # Add serialized batch data to response
                    else:
                        pass
                        # print(f"No BatchMix found with batchName: {batch_material}")
                else:
                    pass
                    # print("Batch name is missing")

                return data
            else:
                # print(f"Unrecognized content type: {content_model}")
                return None
        else:
            # print("Missing content_type or object_id")
            return None

    # def get_ingredient(self, obj):
    #     SERIALIZER_MAP = {
    #         'material': MaterialSerializer,
    #         'processstore': ProcessStoreSerializer,
    #     }
    #     if obj.content_type and obj.object_id:
    #         content_model = obj.content_type.model
    #         serializer_class = SERIALIZER_MAP.get(content_model)
    #         if serializer_class:
    #             # Serialize ingredient data
    #             data = serializer_class(obj.ingredient).data
    #
    #             # Extract the `batch_name` from the current object
    #             batch_name = obj.batch_name
    #             print(batch_name,'------------data name')
    #             # Check if the batch_name exists in the `BatchMix` model
    #             batch_instance = BatchMix.objects.filter(batchName__in=batch_name) # Adjusted query for batch_name
    #
    #             if batch_instance:
    #                 # Serialize the full batch data
    #                 batch_data = BatchMixNewDetailsSerializer(batch_instance,many=True).data
    #                 print(batch_data, '-------Batch data')
    #
    #                 # Include batch data in the ingredient response
    #                 data['batch_data'] = batch_data  # Add serialized batch data to response
    #
    #             return data
    #         else:
    #             print(f"Unrecognized content type: {content_model}")
    #             return None
    #     else:
    #         print("Missing content_type or object_id")
    #         return None
    # def get_ingredient(self, obj):
    #     SERIALIZER_MAP = {
    #         'material': MaterialSerializer,
    #         'processstore': ProcessStoreSerializer,
    #     }
    #     if obj.content_type and obj.object_id:
    #         content_model = obj.content_type.model
    #         print("content object", content_model)
    #         serializer_class = SERIALIZER_MAP.get(content_model)
    #         if serializer_class:
    #             # Serialize ingredient data
    #             data = serializer_class(obj.ingredient).data
    #             print(data, '----DATA')
    #
    #             # Extract batch ID from the serialized ingredient data
    #             batch_id = data.get('batch')
    #             if batch_id:
    #                 print(obj,'---------gaga')
    #                 # Query BatchMix model using the batch ID
    #                 batch_instance = BatchMix.objects.filter(id=batch_id,batchName=obj.batch_name)
    #                 if batch_instance:
    #                     # Serialize the full batch data
    #                     batch_data = BatchMixNewDetailsSerializer(batch_instance,many=True).data
    #                     print(batch_data, '-------Batch data')
    #                     # Include batch data in the ingredient response
    #                     data['batch'] = batch_data
    #                 else:
    #                     print(f"No BatchMix found with id: {batch_id}")
    #             else:
    #                 print("Batch ID not found in ingredient data")
    #
    #             return data
    #         else:
    #             print(f"Unrecognized content type: {content_model}")
    #             return None
    #     else:
    #         print("Missing content_type or object_id")
    #         return None



# Serializer for the BatchMixChocolateIceCreamTemplateForSyrupAndSauce model
class GETBatchMixChocolateIceCreamTemplateSerializer(serializers.ModelSerializer):
    # Prefetch related ingredients
    ingredients = GETBatchMixChocolateIceCreamTemplateIngredientsSerializer(many=True, read_only=True)
    # Include subCategory name
    category_name = serializers.CharField(source='subCategory.category.name', read_only=True)

    class Meta:
        model = BatchMixChocolateIceCreamTemplate
        # fields = ['batchName', 'batchCode', 'expDays', 'subCategory_name', 'ingredients', 'is_deleted']
        fields = ['id','batchName', 'batchCode', 'expDays', 'subCategory', 'ingredients', 'is_deleted', 'category_name']
        depth = 2



# ======================================update==================
from rest_framework import serializers


class BatchMixTemplateIngredientsChocolateUpdateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)

    class Meta:
        model = BatchMixChocolateIceCreamTemplateIngredients
        fields = ['id', 'object_id', 'content_type', 'type', 'lowerLimit', 'percentage', 'upperLimit']

    def validate_content_type(self, value):
        if value not in ["RMStore", "ProcessStore"]:
            raise serializers.ValidationError(f"Invalid content type: {value}")
        return value


class BatchMixTemplateChocolateUpdateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixTemplateIngredientsChocolateUpdateSerializer(many=True)

    class Meta:
        model = BatchMixChocolateIceCreamTemplate
        fields = ['id', 'batchName', 'batchCode', 'expDays', 'subCategory', 'ingredients']

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])

        # Update BatchMixTemplate fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

