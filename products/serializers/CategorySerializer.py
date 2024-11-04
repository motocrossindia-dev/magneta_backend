from django.db.models import Q
from rest_framework import serializers
from products.models import Category, Subcategory


class GETCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class POSTCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate(self, data):
        """
        Check if a category with the same name already exists.
        """
        name = data.get('name')
        if Category.objects.filter(Q(name__iexact=name)).exists():
            raise serializers.ValidationError({"name": ["Category with this name already exists."]})
        return data

    def to_representation(self, instance):
        return super().to_representation(instance)


class PATCHCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate(self, data):
        """
        Check if a category with the same name already exists.
        """
        name = data.get('name')
        if name:
            if Category.objects.filter(Q(name__iexact=name) & ~Q(pk=self.context.get('id'))).exists():
                raise serializers.ValidationError({"name": ["Category with this name already exists."]})

        return data
