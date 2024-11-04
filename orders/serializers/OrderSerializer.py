from rest_framework import serializers

from orders.models import Order, MainOrders, GST


class GETordersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def get_price_per_carton(self, obj):
        price = float(obj.product_name.price)
        carton_size = float(obj.product_name.carton_size)
        return float('{:.2f}'.format(price * carton_size))

    def get_product_name(self, obj):
        return obj.product_name.product_name if obj.product_name else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation.pop('discount_rate', None)
        representation.pop('discounted_price', None)

        representation['price_per_carton'] = self.get_price_per_carton(instance)
        representation['product_name'] = self.get_product_name(instance)

        # Get the product object
        product = instance.product_name

        # Include product name
        # representation['product_name'] = self.get_product_name(instance)

        # Include product image URL if available
        if product and product.image:
            representation['product_image'] = product.image.url
        else:
            representation['product_image'] = None

        return representation


class GETnameDateSerializer(serializers.ModelSerializer):
    grand_total=serializers.SerializerMethodField()
    pending_amount=serializers.SerializerMethodField()

    class Meta:
        model = MainOrders
        # fields = ('id', 'order_date', 'status', 'mode_of_payment', 'grand_total')
        fields = "__all__"

    def get_grand_total(self, obj):
        if obj.mode_of_payment.lower() in ["free sample", "paid", "canceled"]:
            grandtotal = 0.0
        else:
            # Calculate your grand_total logic here
            grandtotal = obj.grand_total
            # Your calculation logic
        return round(grandtotal, 2)

    def get_pending_amount(self, obj):

        if obj.mode_of_payment.lower() in ["free sample", "paid", "canceled"]:
            pending_amount = 0.0
        else:
            pending_amount = obj.pending_amount  # Your calculation logic
        return round(pending_amount, 2)


    def get_name(self, obj):
        return f"{obj.distributor.first_name} {obj.distributor.last_name}" if obj.distributor else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = self.get_name(instance)
        order_date = instance.order_date.strftime("%d-%m-%Y")
        representation['order_date'] = order_date
        gst = GST.objects.get(id=1)

        distributor = instance.distributor

        distributor_gst_number = distributor.gst

        if distributor_gst_number[:2] == "29":
            representation['GST'] = gst.gst
        elif distributor_gst_number[:2] == "" or distributor_gst_number is None:
            representation['CGST'] = gst.cgst
            representation['SGST'] = gst.sgst
        else:
            if representation['IGST'] == 0.00 or representation['IGST'] is None:
                representation['IGST'] = gst.igst
        return representation


class PATCHordersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('accepted_quantity', 'discount_amount', 'factory_base_price', 'factory_gst_price', 'factory_sale',
                  'mrp', 'sum', 'CGST', 'SGST', 'IGST', 'gst', 'amount')

    def to_internal_value(self, data):
        if 'discount' in data and data['discount'] is None:
            data['discount'] = 0
        return super().to_internal_value(data)


class POSTOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['main_order', 'product_name', 'requested_quantity', 'accepted_quantity',
                  'carton_size', 'price_per_carton', 'discount']


class POSTdirectFactoryOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['main_order', 'product_name', 'requested_quantity', 'accepted_quantity',
                  'carton_size', 'price_per_carton', 'discount', 'factory_base_price', 'factory_gst_price',
                  'factory_sale', 'mrp', 'sum', 'CGST', 'SGST', 'IGST', 'gst', 'amount']

    def to_internal_value(self, data):
        if 'discount' in data and data['discount'] is None:
            data['discount'] = 0
        return super().to_internal_value(data)
