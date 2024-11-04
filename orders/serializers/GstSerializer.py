from rest_framework import serializers

from orders.models import GST


class GETgstSerializer(serializers.ModelSerializer):
    class Meta:
        model = GST
        fields = '__all__'


class PATCHgstSerializer(serializers.ModelSerializer):
    class Meta:
        model = GST
        fields = '__all__'