from rest_framework import serializers

from inventory.models import Type


class GETtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class POSTtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'
