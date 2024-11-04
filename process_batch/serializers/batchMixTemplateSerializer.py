from symtable import Class

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from inventory.models import Material
from process_batch.models import BatchMix
from process_batch.models.batchMixTemplate import BatchMixTemplateIngredients, \
    BatchMixTemplate
from process_batch.models.categories import BatchMixSubCategory
from process_store.models import ProcessStore


class BatchMixTemplateIngredientsSerializer(serializers.ModelSerializer):
    type = serializers.CharField()  # Model type passed from frontend
    ingredient_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BatchMixTemplateIngredients
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
        ingredient = BatchMixTemplateIngredients.objects.create(
            content_type=content_type.pk,
            object_id=ingredient_id,
            **validated_data
        )

        return ingredient


class BatchMixTemplateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixTemplateIngredientsSerializer(many=True)
    subCategory = serializers.PrimaryKeyRelatedField(queryset=BatchMixSubCategory.objects.all(), required=False)


    class Meta:
        model = BatchMixTemplate
        fields = '__all__'
        depth = 1


    def create(self, validated_data):
        print(validated_data,'--------------------data')
        # Extract the list of ingredients from the validated data
        ingredients_data = validated_data.pop('ingredients')

        # Create the BatchMixTemplateForSyrupAndSauce instance
        batch_template = BatchMixTemplate.objects.create(**validated_data)

        # Create each ingredient entry and associate it with the batch_template
        for ingredient_data in ingredients_data:
            ingredient_type = ingredient_data.pop('content_type')
            ingredient_id = ingredient_data.pop('ingredient_id')

            # Create the ingredient with the correct content_type and object_id
            BatchMixTemplateIngredients.objects.create(
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

# Serializer for the BatchMixTemplateIngredientsForSyrupAndSauce model
class GETBatchMixTemplateIngredientsSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()

    class Meta:
        model = BatchMixTemplateIngredients
        fields ="__all__"
        # fields = ['type', 'lowerLimit', 'percentage', 'upperLimit', 'ingredient']
        depth = 3



    def get_ingredient(self, obj):
        SERIALIZER_MAP = {
            'material': MaterialSerializer,
            'processstore': ProcessStoreSerializer,
        }
        if obj.content_type and obj.object_id:
            content_model = obj.content_type.model
            serializer_class = SERIALIZER_MAP.get(content_model)
            if serializer_class:
                return serializer_class(obj.ingredient).data
            else:
                print(f"Unrecognized content type: {content_model}")
                return None
        else:
            print("Missing content_type or object_id")
            return None

    # def get_ingredient(self, obj):
    #     return contenttypeSerializer(obj.content_type).data
    #     print(obj.ingredient, "obj.ingredient before isinstance", obj.content_type.model, obj.object_id)
    #     if obj.content_type and obj.object_id:
    #         if obj.content_type.model == 'material':
    #             return MaterialSerializer(obj.ingredient).data
    #         elif obj.content_type.model == 'ProcessStore':  # "processStoreSyrupAndSauce" check whether its coming correctly
    #             data_to_return = ProcessStoreSerializer(obj.ingredient).data
    #             return data_to_return
    #         else:
    #             return None
    #     else:
    #         return None


# Serializer for the BatchMixTemplateForSyrupAndSauce model
class GETBatchMixTemplateSerializer(serializers.ModelSerializer):
    # Prefetch related ingredients
    ingredients = GETBatchMixTemplateIngredientsSerializer(many=True, read_only=True)
    # Include subCategory name
    category_name = serializers.CharField(source='subCategory.category.name', read_only=True)

    class Meta:
        model = BatchMixTemplate
        # fields = ['batchName', 'batchCode', 'expDays', 'subCategory_name', 'ingredients', 'is_deleted']
        fields = ['id','batchName', 'batchCode', 'expDays', 'subCategory', 'ingredients', 'is_deleted', 'category_name']
        depth = 2

# ======================================update==================
from rest_framework import serializers


class BatchMixTemplateIngredientsUpdateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)

    class Meta:
        model = BatchMixTemplateIngredients
        fields = ['id', 'object_id', 'content_type', 'type', 'lowerLimit', 'percentage', 'upperLimit']

    def validate_content_type(self, value):
        if value not in ["RMStore", "ProcessStore"]:
            raise serializers.ValidationError(f"Invalid content type: {value}")
        return value


class BatchMixTemplateUpdateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixTemplateIngredientsUpdateSerializer(many=True)

    class Meta:
        model = BatchMixTemplate
        fields = ['id', 'batchName', 'batchCode', 'expDays', 'subCategory', 'ingredients']

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])

        # Update BatchMixTemplate fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance