from rest_framework import serializers
from sales.models import ProductDiscount

class ProductDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = '__all__'  # Include all fields or specify specific ones if needed
