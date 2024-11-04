import pandas as pd
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Export Product data to an Excel file'

    def handle(self, *args, **kwargs):
        queryset = Product.objects.all()

        data = list(queryset.values(
            'product_name',
            'subcategory__name',
            'category',
            'description',
            'image',
            'price',
            'carton_size',
            'product_barcode',
            'carton_barcode',
            'is_active',
            'gst',
            'factory_gst',
            'factory_sale',
            'distributor_margin_rate',
            'distributor_margin_price',
            'distributor_gst',
            'distributor_sale',
            'retailer_margin_rate',
            'retailer_margin_price',
            'retailer_gst',
            'retailer_sale',
            'retailer_base_price',
            'retailer_base_gst',
            'mrp',
        ))

        df = pd.DataFrame(data)

        output_file = 'products_export.xlsx'
        df.to_excel(output_file, index=False)

        self.stdout.write(self.style.SUCCESS(f'Successfully exported data to {output_file}'))
