from rest_framework import serializers
from orders.models import FactoryToCustomer


class POSTfactoryToCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryToCustomer
        fields = ['order_number', 'sold_by', 'product_name', 'order_date', 'mode_of_payment', 'payment_status',
                  'quantity', 'mrp', 'amount']


class GETfactoryToCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryToCustomer
        fields = ['order_number', 'sold_by', 'product_name', 'order_date', 'mode_of_payment', 'payment_status',
                  'quantity', 'mrp', 'amount']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_name'] = instance.product_name.product_name
        representation['sold_by'] = f"{instance.sold_by.first_name} {instance.sold_by.last_name}"
        
        return representation
