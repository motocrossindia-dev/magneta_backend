from rest_framework import serializers

from retailers.models import CustomerMainOrders


class GETcustomerMainOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerMainOrders
        fields = '__all__'


class POSTcustomerMainOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerMainOrders
        fields = ['orderDate', 'modeOfPayment', 'customerFullName', 'customerPhoneNumber', 'orderNumber']

    def validate(self, data):
        if 'request' in self.context:
            ordered_products = self.context['request']
            if not ordered_products:
                raise serializers.ValidationError("Ordered products cannot be empty")
        return data
