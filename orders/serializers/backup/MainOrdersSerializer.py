from rest_framework import serializers

from orders.models import MainOrders


class GETmainOrdersSerializer(serializers.ModelSerializer):
    first_name_id = serializers.SerializerMethodField()

    class Meta:
        model = MainOrders
        fields = '__all__'

    def get_first_name_id(self, obj):
        if obj.distributor and obj.distributor.user_id:
            user_id = obj.distributor.user_id.split('-')[-1]  # Extracting the user id
            return f"{obj.distributor.first_name}_{user_id}"
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation.pop('first_name_id', None)
        representation.pop('created', None)
        representation.pop('updated', None)
        representation.pop('distributor', None)
        representation['name_id'] = self.get_first_name_id(instance)

        representation['order_date'] = instance.order_date.strftime('%d-%m-%Y')
        representation['bill_amount'] = 10000
        return representation


class POSTMainOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainOrders
        fields = ['distributor', 'order_date', 'status', 'mode_of_payment', 'payment_status']

    def validate(self, data):
        if 'request' in self.context:
            ordered_products = self.context['request']
            if not ordered_products:
                raise serializers.ValidationError("Ordered products cannot be empty")
        return data


class PATCHmainOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainOrders
        fields = ['status', 'mode_of_payment']
