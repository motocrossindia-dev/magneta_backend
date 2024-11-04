from rest_framework import serializers

from process_batch.models.categories import BatchMixSubCategory, BatchMixCategory


class BatchMixCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchMixCategory
        fields = "__all__"


class BatchMixSubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = BatchMixSubCategory
        fields = "__all__"
