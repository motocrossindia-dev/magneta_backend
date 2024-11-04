# products/management/commands/fill_product_ids.py

from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Fills the product_id column for products.'

    def handle(self, *args, **options):
        products = Product.objects.all()
        for idx, product in enumerate(products):
            product.product_id = idx + 1
            product.save()

        self.stdout.write(self.style.SUCCESS('Successfully filled product_ids.'))
