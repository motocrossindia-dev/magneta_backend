from rest_framework import serializers

from retailers.models import CustomerOrders


class GETcustomerOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOrders
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        product = instance.productId

        if product and product.image:
            representation['product_image'] = product.image.url
        else:
            representation['product_image'] = None

        return representation


class POSTcustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOrders
        fields = '__all__'
