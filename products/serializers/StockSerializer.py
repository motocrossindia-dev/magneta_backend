from rest_framework import serializers

from distributors.models import DistributorStock


class GETstockSerializer(serializers.ModelSerializer):

    class Meta:
        model = DistributorStock
        fields = ['product_id', 'quantity']