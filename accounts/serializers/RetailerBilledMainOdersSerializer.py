from rest_framework import serializers

from distributors.models import RetailerMainOrders


class GETretailerBilledMainOrdersSerializer(serializers.ModelSerializer):
    first_name_id = serializers.SerializerMethodField()

    class Meta:
        model = RetailerMainOrders
        fields = '__all__'

    def get_first_name_id(self, obj):
        if obj.retailer and obj.retailer.user_id:
            user_id = obj.retailer.user_id.split('-')[-1]  # Extracting the user id
            return f"{obj.retailer.first_name}_{user_id}"
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation.pop('created', None)
        representation.pop('updated', None)
        representation.pop('retailer', None)
        representation['retailer_name_id'] = self.get_first_name_id(instance)

        return representation
