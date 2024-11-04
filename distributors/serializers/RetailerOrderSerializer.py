from rest_framework import serializers

from distributors.models import RetailerOrders
from products.models import Product


class GETretailerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetailerOrders
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        product = instance.product_id

        if product and product.image:
            representation['product_image'] = product.image.url
        else:
            representation['product_image'] = None
        representation['mode_of_payment'] = instance.retailer_main_order.mode_of_payment
        representation['payment_status'] = instance.retailer_main_order.payment_status

        return representation


class POSTretailerOrderSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        print(attrs,'==========VALIDATE== ')
        product=self.context['ordered_product_data']
        print(product,'-=======================product')

        try:
            product_instance=Product.objects.get(id=product.get('product_id'))
            product_instance.product_discount=product.get('product_discount',0.0)
            product_instance.save()
        except:
            return serializers.ValidationError({'message':'Product does not exist'})


        return attrs
    class Meta:
        model = RetailerOrders
        fields = '__all__'
