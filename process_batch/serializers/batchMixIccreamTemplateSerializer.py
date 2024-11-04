from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from inventory.models import Material
from process_batch.models.BatchMixIceCream import BatchMixIceCreamTemplateIngredients, BatchMixIceCreamTemplate
from process_batch.models.categories import BatchMixSubCategory
from process_batch.serializers.batchMixTemplateSerializer import MaterialSerializer, ProcessStoreSerializer
from process_store.models import ProcessStore

class BatchMixIceCreamTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchMixIceCreamTemplate
        fields = ['batchName','batchCode','expDays','subCategory',]

# Serializer for the BatchMixTemplateIngredientsForSyrupAndSauce model
class GETBatchMixIceCreamTemplateIngredientsSerializer(serializers.ModelSerializer):
    ingredient = serializers.SerializerMethodField()
    template = BatchMixIceCreamTemplateSerializer(read_only=True)

    class Meta:
        model = BatchMixIceCreamTemplateIngredients
        fields ="__all__"
        # fields = ['type', 'lowerLimit', 'percentage', 'upperLimit', 'ingredient']
        # depth = 1

    def get_ingredient(self, obj):
        # print(obj.ingredient, "obj.ingredient before isinstance", obj.content_type.model, obj.object_id)
        if obj.content_type and obj.object_id:
            if obj.content_type.model == 'material':
                return MaterialSerializer(obj.ingredient).data
            elif obj.content_type.model == 'ProcessStore':  # "processStoreSyrupAndSauce" check whether its coming correctly
                data_to_return = ProcessStoreSerializer(obj.ingredient).data
                return data_to_return
            else:
                return None
        else:
            return None


# Serializer for the BatchMixTemplateForSyrupAndSauce model
class GETBatchMixIceCreamTemplateSerializer(serializers.ModelSerializer):
    # Prefetch related ingredients
    ingredients = GETBatchMixIceCreamTemplateIngredientsSerializer(many=True, read_only=True)

    # Include subCategory name
    category_name = serializers.CharField(source='subCategory.category.name', read_only=True)

    class Meta:
        model = BatchMixIceCreamTemplate
        fields = "__all__"
        # fields = ['batchName', 'batchCode', 'expDays', 'subCategory_name', 'ingredients', 'is_deleted']
        # fields = ['id','batchName', 'batchCode', 'expDays', 'subCategory', 'ingredients', 'is_deleted', 'category_name',]
        depth = 2

# ============================post


class BatchMixIceCreamTemplateIngredientsSerializer(serializers.ModelSerializer):
    type = serializers.CharField()  # Model type passed from frontend
    ingredient_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BatchMixIceCreamTemplateIngredients
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
        ingredient = BatchMixIceCreamTemplateIngredients.objects.create(
            content_type=content_type.pk,
            object_id=ingredient_id,
            **validated_data
        )

        return ingredient


class BatchMixIceCreamTemplateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixIceCreamTemplateIngredientsSerializer(many=True)
    subCategory = serializers.PrimaryKeyRelatedField(queryset=BatchMixSubCategory.objects.all(), required=False)

    class Meta:
        model = BatchMixIceCreamTemplate
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data,'------------ice creaam--------data')
        # Extract the list of ingredients from the validated data
        ingredients_data = validated_data.pop('ingredients')

        # Create the BatchMixIceCreamTemplateForSyrupAndSauce instance
        batch_template = BatchMixIceCreamTemplate.objects.create(**validated_data)

        # Create each ingredient entry and associate it with the batch_template
        for ingredient_data in ingredients_data:
            ingredient_type = ingredient_data.pop('content_type')
            ingredient_id = ingredient_data.pop('ingredient_id')

            # Create the ingredient with the correct content_type and object_id
            BatchMixIceCreamTemplateIngredients.objects.create(
                template=batch_template,
                content_type=ingredient_type,
                # object_id=ingredient_id,
                **ingredient_data
            )
        return batch_template

# ====================update=========================

class BatchMixIceCreamTemplateIngredientsUpdateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)

    class Meta:
        model = BatchMixIceCreamTemplateIngredients
        fields = ['id', 'object_id', 'content_type', 'type', 'lowerLimit', 'percentage', 'upperLimit']

    def validate_content_type(self, value):
        if value not in ["RMStore", "ProcessStore"]:
            raise serializers.ValidationError(f"Invalid content type: {value}")
        return value


class BatchMixIceCreamTemplateUpdateSerializer(serializers.ModelSerializer):
    ingredients = BatchMixIceCreamTemplateIngredientsUpdateSerializer(many=True)

    class Meta:
        model = BatchMixIceCreamTemplate
        fields = [
            'id', 'batchName', 'batchCode', 'expDays', 'subCategory',
            'milk_fat_percentage', 'milk_snf_percentage', 'batch_fat_percentage',
            'batch_snf_percentage', 'cream_percentage', 'butter_percentage',
            'smp_snf_percentage', 'standard_converstion_factor', 'ingredients'
        ]

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])

        # Update BatchMixIceCreamTemplate fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance