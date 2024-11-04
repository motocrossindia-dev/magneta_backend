from django.db.models import Q
from rest_framework import serializers

from distributors.models import DistributorStock
from products.models import Product, ProductImage, ProductSize, ProductFlavour, ProductSpecification
from django.utils.translation import gettext_lazy as _


class ProductFlavourSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFlavour
        fields = '__all__'


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = '__all__'

    def validate(self, data):
        """
        Check if size_name and size_volume are not blank.
        """
        if 'size_name' in data and not data['size_name'].strip():
            raise serializers.ValidationError("size_name cannot be blank.")

        if 'size_volume' in data and not data['size_volume'].strip():
            raise serializers.ValidationError("size_volume cannot be blank.")

        return data


class GETProductSerializer(serializers.ModelSerializer):
    distributor_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_distributor_quantity(self, instance):
        request = self.context.get('request', None)
        if request and request.user.is_distributor:
            distributor_id = request.user.id
            try:
                distributor_stock = DistributorStock.objects.get(distributor_id=distributor_id, product_id=instance.id)
                return distributor_stock.quantity
            except DistributorStock.DoesNotExist:
                return None
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Replace category ID with category name

        product_flavour = instance.product_flavours.first()  # Get the first product flavour
        if product_flavour:
            representation['flavour_name'] = product_flavour.flavour_name

        size_and_volume = instance.product_sizes.first()  # Get the first product size
        if size_and_volume:
            representation['size_name'] = size_and_volume.size_name
            representation['size_volume'] = size_and_volume.size_volume

        specification = instance.product_specifications.first()  # Get the first product specification
        if specification:
            representation['specification_name'] = specification.specification_name

        representation['subcategory_name'] = instance.subcategory.name
        representation['category_id'] = instance.subcategory.category.id
        representation['category_name'] = instance.subcategory.category.name

        representation['image'] = instance.image.url
        representation['distributor_quantity'] = self.get_distributor_quantity(instance)

        return representation


class POSTProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate(self, data):

        errors = {}
        image = data.get('image', None)
        if image:
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                errors["image"] = _("The file is not an image.")
        else:
            errors["image"] = _("The image field is required.")

        product_name = data.get('product_name')
        if Product.objects.filter(Q(product_name__iexact=product_name)).exists():
            errors["product_name"] = ["Product with this name already exists"]

        # min_price = data.get('min_price')
        price = data.get('price')
        carton_size = data.get('carton_size')

        if price is not None and float(price) <= 0:
            errors["price"] = ["Price must be greater than 0."]

        if carton_size is not None and int(carton_size) <= 0:
            errors["carton_size"] = ["Carton size must be greater than 0."]

        # Raise validation error if there are any errors accumulated
        if errors:
            raise serializers.ValidationError(errors)

        return data


class PATCHProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['image']

    def validate(self, data):
        """
        Validate the data before saving.
        """
        product_name = data.get('product_name')
        if product_name:
            if Product.objects.filter(Q(product_name__iexact=product_name) & ~Q(pk=self.context.get('id'))).exists():
                raise serializers.ValidationError({"product_name": ["Product with this name already exists."]})

        min_price = data.get('min_price')
        price = data.get('price')

        if min_price is not None and float(min_price) <= 0:
            raise serializers.ValidationError({"min_price": ["Minimum price must be greater than 0."]})

        if price is not None and float(price) <= 0:
            raise serializers.ValidationError({"price": ["Price must be greater than 0."]})

        return data


class ChangeProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['image']

