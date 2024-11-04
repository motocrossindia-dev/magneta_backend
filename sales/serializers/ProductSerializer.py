from rest_framework import serializers

from distributors.models import DistributorStock
from products.models import Product
from sales.models import distributor_sales


class GETProductSerializer(serializers.ModelSerializer):
    distributor_quantity = serializers.SerializerMethodField()
    distributor_base_price=serializers.SerializerMethodField()
    distributor_carton_base_price=serializers.SerializerMethodField()
    distributor_carton_gst_price=serializers.SerializerMethodField()
    distributor_carton_sale_price=serializers.SerializerMethodField()

    def get_distributor_base_price(self,obj):
        price=obj.distributorBasePrice or 0.0
        return price

    def get_distributor_carton_base_price(self,obj):
        price=obj.distributorCartonBasePrice or 0.0
        return price

    def get_distributor_carton_gst_price(self,obj):
        price=obj.distributorCartonGstPrice or 0.0
        return price
    def get_distributor_carton_sale_price(self,obj):
        price=obj.distributorCartonSalePrice or 0.0
        return price

    class Meta:
        model = Product
        fields = '__all__'

    def get_distributor_quantity(self, instance):
        request = self.context.get('request', None)
        if request and request.user.is_distributor:
            if request.user.role.role != 'sales':
                distributor_id = request.user.id
            else:
                print(request.user)
                sales_person = distributor_sales.objects.get(sales_person=request.user)
                # sales_person.distributor.id
                distributor_id = sales_person.distributor.id
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
# from rest_framework import serializers

# from distributors.models import DistributorStock
# from products.models import Product
# from sales.models import distributor_sales


# class GETProductSerializer(serializers.ModelSerializer):
#     distributor_quantity = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = '__all__'

#     def get_distributor_quantity(self, instance):
#         request = self.context.get('request', None)
#         if request and request.user.is_distributor:
#             if request.user.role.role != 'sales':
#                 print("not salse==========1")
#                 distributor_id = request.user.id
#             else:
#                 print(request.user)
#                 sales_person = distributor_sales.objects.filter(sales_person=request.user).first()
#                 # sales_person.distributor.id
#                 distributor_id = sales_person.distributor.id

#             try:
#                 distributor_stock = DistributorStock.objects.filter(distributor_id=distributor_id, product_id=instance.id).first()
#                 return distributor_stock.quantity
#             except DistributorStock.DoesNotExist:
#                 return None
#         return None

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         # Replace category ID with category name

#         product_flavour = instance.product_flavours.first()  # Get the first product flavour
#         if product_flavour:
#             representation['flavour_name'] = product_flavour.flavour_name

#         size_and_volume = instance.product_sizes.first()  # Get the first product size
#         if size_and_volume:
#             representation['size_name'] = size_and_volume.size_name
#             representation['size_volume'] = size_and_volume.size_volume

#         specification = instance.product_specifications.first()  # Get the first product specification
#         if specification:
#             representation['specification_name'] = specification.specification_name

#         representation['subcategory_name'] = instance.subcategory.name
#         representation['category_id'] = instance.subcategory.category.id
#         representation['category_name'] = instance.subcategory.category.name

#         representation['image'] = instance.image.url
#         representation['distributor_quantity'] = self.get_distributor_quantity(instance)

#         return representation
