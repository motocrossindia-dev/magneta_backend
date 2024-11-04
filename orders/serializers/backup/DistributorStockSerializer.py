from rest_framework import serializers

from distributors.models import DistributorStock


class GETdistributorStockSerializer(serializers.ModelSerializer):

    class Meta:
        model = DistributorStock
        fields = ['quantity', 'updated']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['updated'] = instance.updated.strftime('%d-%m-%Y')
        representation['product_name'] = instance.product_id.product_name
        return representation
