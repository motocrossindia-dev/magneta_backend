from rest_framework import serializers
from products.models import Category, Subcategory


class GETMRPCalculationResultSerializer(serializers.Serializer):
    gst = serializers.DecimalField(max_digits=10, decimal_places=2)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    factory_gst = serializers.DecimalField(max_digits=10, decimal_places=2)
    factory_sale = serializers.DecimalField(max_digits=10, decimal_places=2)
    distributor_margin_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    distributor_margin_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    distributor_gst = serializers.DecimalField(max_digits=10, decimal_places=2)
    distributor_sale = serializers.DecimalField(max_digits=10, decimal_places=2)
    retailer_margin_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    retailer_margin_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    retailer_gst = serializers.DecimalField(max_digits=10, decimal_places=2)
    retailer_sale = serializers.DecimalField(max_digits=10, decimal_places=2)
    retailer_base_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    retailer_base_gst = serializers.DecimalField(max_digits=10, decimal_places=2)
    mrp = serializers.DecimalField(max_digits=10, decimal_places=2)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request_data = self.context

        representation['product_name'] = request_data.get('product_name')
        representation['product_barcode'] = request_data.get('product_barcode')
        representation['carton_barcode'] = request_data.get('carton_barcode')
        representation['category'] = request_data.get('category')
        representation['subcategory'] = request_data.get('subcategory')
        representation['size_volume'] = request_data.get('size_volume')
        representation['size_name'] = request_data.get('size_name')
        representation['flavour_name'] = request_data.get('flavour_name')
        representation['carton_size'] = request_data.get('carton_size')
        representation['is_active'] = True if request_data.get('is_active') == 'true' else False
        return representation
