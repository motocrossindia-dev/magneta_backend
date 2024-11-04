import os
import shutil
import shutil
from django.core.files import File
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.core.files import File
from rest_framework import serializers, status

from StockReport.models import ProductStockRecord, StockRecord, OpeningStock
from StockReport.pdf_generator import generate_comprehensive_stock_pdf
from products.models import Product, ProductSize


# <editor-fold desc="products records get">
class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['size_name', 'size_volume']
class ProductsSerializer(serializers.ModelSerializer):
    size_volume = serializers.SerializerMethodField()
    opening_stock_units = serializers.SerializerMethodField()
    opening_stock_lits = serializers.SerializerMethodField()
    lit_fact = serializers.SerializerMethodField()

    def get_size_volume(self, obj):
        size = obj.product_sizes.all().first()
        return size.size_volume if size else None

    def get_opening_stock_units(self, obj):
        stock_record = OpeningStock.objects.filter(product=obj).first()
        return stock_record.physical_stock if stock_record and stock_record.physical_stock != 0 else (stock_record.closing_stock if stock_record else 0)

    def get_opening_stock_lits(self, obj):
        stock_record = obj.stock_records.first()
        return stock_record.opening_stock_lits if stock_record else 0

    def get_lit_fact(self, obj):
        if obj.product_sizes.exists():
            first_size = obj.product_sizes.first()
            volume = float(first_size.size_volume)
            return (volume * obj.carton_size) / 1000
        return None

    class Meta:
        model = Product
        fields = '__all__'

# </editor-fold>

import logging

logger = logging.getLogger(__name__)
# <editor-fold desc="product stock create">
class ProductStockRecordGetCreateSerializer(serializers.Serializer):
    """
    Serializer for creating and updating ProductStockRecord with nested OpeningStock data.
    """
    product = serializers.IntegerField()
    volume_nos = serializers.FloatField()
    mrp = serializers.FloatField()
    lit_factor = serializers.FloatField()

    # Opening stock fields (nested)
    opening_stock_units = serializers.FloatField()
    opening_stock_lits = serializers.FloatField()
    opening_stock_value = serializers.FloatField()

    # Production data
    production_units = serializers.FloatField()
    production_lits = serializers.FloatField()
    production_value = serializers.FloatField()

    # Sales data
    sales_units = serializers.FloatField()
    sales_lits = serializers.FloatField()
    sales_value = serializers.FloatField()

    # Closing stock data
    closing_stock_units = serializers.FloatField()
    closing_stock_lits = serializers.FloatField()
    closing_stock_value = serializers.FloatField()


    damage_in_units=serializers.FloatField(default=0.0)
    return_in_units=serializers.FloatField(default=0.0)

    # Other fields
    physical_stock = serializers.FloatField()
    comments = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        fields = '__all__'

    def validate(self, attrs):

        print(attrs,'---------------data')
        """
        Custom validation logic.
        """
        product_id = attrs.get('product')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")

        # Additional validation can be added here if needed.

        return attrs
class ProductStockRecordCreateSerializer(serializers.Serializer):
    """
    Serializer for creating ProductStockRecord instances.
    """
    date = serializers.DateField(write_only=True)
    products = ProductStockRecordGetCreateSerializer(many=True, write_only=True)

    def validate(self, attrs):
        date = attrs.get('date')
        if StockRecord.objects.filter(date=date).exists():
            raise serializers.ValidationError(f"A StockRecord for {date} already exists.")
        return attrs

    def create(self, validated_data):
        date = validated_data.pop('date')
        products_data = validated_data.pop('products')

        stock_record, created = StockRecord.objects.get_or_create(
            date=date,
            defaults={'generated_file': None}
        )

        for product_data in products_data:
            product_id = product_data.pop('product')
            product = Product.objects.get(id=product_id)

            product_stock_record, _ = ProductStockRecord.objects.update_or_create(
                product=product,
                stock_record=stock_record,
                defaults=product_data
            )

            OpeningStock.objects.update_or_create(
                product=product,
                defaults={
                    'opening_stock': product_stock_record.opening_stock_units,
                    'closing_stock': product_stock_record.closing_stock_units - product_stock_record.damage_in_units+product_stock_record.return_in_units,
                    'physical_stock': product_stock_record.physical_stock
                }
            )


        try:
            # Generate the PDF using the existing function
            original_pdf_path = generate_comprehensive_stock_pdf(stock_record)

            # Create stock_reports directory if it doesn't exist
            reports_dir = os.path.join(settings.MEDIA_ROOT, 'stock_reports')
            os.makedirs(reports_dir, exist_ok=True)

            # Generate a new file name
            timestamp = timezone.now().strftime('%d%m%Y_%H%M%S')
            new_pdf_filename = f"stock_report_{stock_record.id}_{timestamp}.pdf"
            new_pdf_path = os.path.join(reports_dir, new_pdf_filename)

            # Move the generated PDF to the stock_reports directory
            shutil.move(original_pdf_path, new_pdf_path)

            # Save the generated file to the model
            with open(new_pdf_path, 'rb') as file:
                stock_record.generated_file.save(new_pdf_filename, File(file))

        except:
            pass

        pdf_filename = generate_comprehensive_stock_pdf(stock_record)

        with open(pdf_filename, 'rb') as file:
            stock_record.generated_file.save(os.path.basename(pdf_filename), File(file))

        return validated_data


# </editor-fold>


# <editor-fold desc="stock records get all and details ">
class ProductsGetSerailizers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
class ProductStockRecordGetedSerilaizers(serializers.ModelSerializer):
    # product_name=serializers.ReadOnlyField(source='product.product_name')
    product=ProductsGetSerailizers()
    class Meta:
        model=ProductStockRecord
        fields='__all__'
class StockRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for the StockRecord model.
    """
    stock_record = ProductStockRecordGetedSerilaizers(many=True, read_only=True,source="product_stock_records")
    # stock_records = serializers.PrimaryKeyRelatedField(many=True, read_only=True,source="product_stock_records")
    date = serializers.DateField(input_formats=['%Y-%m-%d', 'iso-8601'])

    class Meta:
        model = StockRecord
        fields = ['id', 'date', 'stock_record', 'generated_file', 'is_editable', 'created_at', 'updated_at']
        read_only_fields = ('is_editable',)
        # depth=2
# </editor-fold>


# <editor-fold desc="product stock record update by id">

from rest_framework import serializers
from .models import StockRecord, ProductStockRecord, Product


class ProductStockRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStockRecord
        fields = ['id', 'product', 'volume_nos', 'mrp', 'lit_factor', 'opening_stock_units',
                  'opening_stock_lits', 'opening_stock_value', 'production_units', 'production_lits',
                  'production_value', 'sales_units', 'sales_lits', 'sales_value', 'closing_stock_units',
                  'closing_stock_lits', 'closing_stock_value', 'physical_stock', 'comments','damage_in_units','return_in_units']


class StockRecordUpdateSerializer(serializers.ModelSerializer):
    products = ProductStockRecordSerializer(many=True,write_only=True)

    # def validate(self, data):
    #     instance = self.instance
    #     if instance and not instance.is_editable:
    #         raise serializers.ValidationError("This stock record is not editable.")
    #     return data

    class Meta:
        model = StockRecord
        fields = ['id', 'date', 'products']

    def update(self, instance, validated_data):
        stock_records_data = validated_data.pop('products', [])
        instance.date = validated_data.get('date', instance.date)
        instance.save()

        for stock_record_data in stock_records_data:
            product_id = stock_record_data.pop('product')
            product = Product.objects.get(id=product_id.id)

            product_stock_record,created =ProductStockRecord.objects.update_or_create(
                stock_record=instance,
                product=product,
                defaults=stock_record_data
            )

            OpeningStock.objects.update_or_create(
                product=product,
                defaults={
                    'opening_stock': product_stock_record.opening_stock_units,
                    'closing_stock': product_stock_record.closing_stock_units,
                    'physical_stock': product_stock_record.physical_stock
                }
            )

        return instance
# </editor-fold>

