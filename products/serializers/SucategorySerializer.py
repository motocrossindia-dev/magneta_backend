from django.db.models import Q
from rest_framework import serializers

from products.models import Subcategory


class GETSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('id', 'name', 'category')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category_name'] = instance.category.name
        representation['category_id'] = instance.category.id
        return representation


class POSTSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'

    def validate(self, data):
        """
        Check if a category with the same name already exists.
        """
        name = data.get('name')
        if Subcategory.objects.filter(Q(name__iexact=name)).exists():
            raise serializers.ValidationError({"name": ["Subcategory with this name already exists."]})

        return data


class PATCHSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'

    def validate(self, data):
        """
        Check if a category with the same name already exists.
        """
        name = data.get('name')
        if name:
            if Subcategory.objects.filter(Q(name__iexact=name) & ~Q(pk=self.context.get('id'))).exists():
                raise serializers.ValidationError({"name": ["Subcategory with this name already exists."]})

        return data
