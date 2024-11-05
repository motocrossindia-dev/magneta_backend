from rest_framework import serializers

from distributors.models import RetailerMainOrders
from sales.models import retailerTransactionDetails


class GETretailerMainOrderSerializer(serializers.ModelSerializer):
    retailer_id = serializers.SerializerMethodField()
    first_name_id = serializers.SerializerMethodField()
    enterpriseName = serializers.SerializerMethodField()
    sub_total=serializers.SerializerMethodField()
    grand_total=serializers.SerializerMethodField()
    pending_amount=serializers.SerializerMethodField()

    retailer_wallet_amount=serializers.SerializerMethodField()
    retailer_total_pending_amount=serializers.SerializerMethodField()
    retailer_total_cancelled_amount=serializers.SerializerMethodField()
    retailer_total_bill_amount=serializers.SerializerMethodField()


    def get_retailer_wallet_amount(self,obj):
        try:
            transaction = retailerTransactionDetails.objects.get(retailer=obj.retailer)
            unused_amount=transaction.amount
        except retailerTransactionDetails.DoesNotExist:
            print("error in getUnusedAmount : DoesNotExist")
            unused_amount= 0.00
        return unused_amount


    def get_retailer_total_pending_amount(self,obj):
        print("retailer grand total")
        total_pending_amount_by_retailer=obj.total_pending_amount_by_retailer(obj.retailer.id)
        return total_pending_amount_by_retailer

    def get_retailer_total_cancelled_amount(self,obj):
        total_cancelled_amount=obj.total_cancelled_amount_by_retailer(obj.retailer.id)
        return total_cancelled_amount

    def get_retailer_total_bill_amount(self,obj):
        total_cancelled_amount=obj.total_bill_amount_by_retailer(obj.retailer.id)
        return total_cancelled_amount




    def get_sub_total(self, obj):
        # Calculate your sub_total logic here
        subtotal = obj.sub_total  # Your calculation logic
        return round(subtotal, 2)

    def get_grand_total(self, obj):
        # =here change
        if obj.mode_of_payment.lower() in ["free sample", "paid", "canceled"] or obj.payment_status.lower() in ["cancelled"]:
            grandtotal = 0.0
        else:
            # Calculate your grand_total logic here
            grandtotal = obj.grand_total
            # Your calculation logic
        return round(grandtotal, 2)

    def get_pending_amount(self, obj):
        # print("order id ",obj.id)
        # print("order mode_of_payment ",obj.mode_of_payment)
        # print("order_payment ",obj.payment_status)

        if obj.mode_of_payment.lower() in ["free sample", "paid", "cancelled"] or obj.payment_status.lower() in ["cancelled"]:
            pending_amount = 0.0
        else:
            pending_amount = obj.pending_amount  # Your calculation logic
        return round(pending_amount, 2)

    class Meta:
        model = RetailerMainOrders
        fields = '__all__'

    def get_first_name_id(self, obj):
        if obj.retailer and obj.retailer.user_id:
            user_id = obj.retailer.enterprise_name # Extracting the user id
            return user_id
        return None
    # def get_first_name_id(self, obj):
    #     if obj.retailer and obj.retailer.user_id:
    #         user_id = obj.retailer.user_id.split('-')[-1]  # Extracting the user id
    #         return f"{obj.retailer.first_name}_{user_id}"
    #     return None
    def get_retailer_id(self, obj):
        if obj.retailer and obj.retailer.user_id:
            user_id = obj.retailer.id
            return user_id
        return None
    def get_enterpriseName(self, obj):
        if obj.retailer and obj.retailer.user_id:
          return obj.retailer.enterprise_name or ''

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation.pop('created', None)
        representation.pop('updated', None)
        representation.pop('retailer', None)
        representation['retailer_name_id'] = self.get_first_name_id(instance)

        return representation


class POSTretailerMainOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetailerMainOrders
        fields = ['retailer', 'order_date', 'mode_of_payment',]

    def validate(self, data):
        if 'request' in self.context:
            ordered_products = self.context['request']
            if not ordered_products:
                raise serializers.ValidationError("Ordered products cannot be empty")
        return data

