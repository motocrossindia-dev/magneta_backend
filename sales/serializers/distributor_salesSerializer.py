from rest_framework import serializers
from sales.models import distributor_sales


class DistributorSalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = distributor_sales
        exclude = ['distributor', 'created', 'updated']
        depth = 2

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        sales_person = representation.get('sales_person')
        if sales_person and 'password' in sales_person:
            sales_person.pop('password')
        return representation
