from rest_framework import serializers

from inventory.models import SubType


class GETsubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubType
        fields = '__all__'


class POSTsubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubType
        fields = '__all__'

    def create(self, validated_data):
        return SubType.objects.create(**validated_data)