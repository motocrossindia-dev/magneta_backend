# retailerTransactionDetails
from rest_framework import serializers

from accounts.models import UserBase
from sales.models import retailerTransactionDetails, salesRetailerTransactions


class retailerTransactionDetailsSerializer(serializers.ModelSerializer):
    retailer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = retailerTransactionDetails
        fields = '__all__'
        # depth =1

    def getretailer(self, obj):
        return obj.retailer.first_name


class GETretailerSerializer(serializers.ModelSerializer):
    transaction_details = serializers.SerializerMethodField()

    class Meta:
        model = UserBase
        fields = ['id', 'user_id', 'first_name', 'phone_number', 'pan', 'gst', 'Address', 'email', 'pincode',
                  'enterprise_name', 'transaction_details']

    def get_transaction_details(self, obj):
        transactions = retailerTransactionDetails.objects.filter(retailer=obj)
        if transactions.exists():
            return retailerTransactionDetailsSerializer(transactions, many=True).data
        return []


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields=['user_id','full_name','phone_number','email']

class salesRetailerTransactionsSerializer(serializers.ModelSerializer):
    retailerName = serializers.SerializerMethodField()
    retailer_id = serializers.SerializerMethodField()
    distributor = serializers.SerializerMethodField()
    sales_person = serializers.SerializerMethodField()
    sales_person_name = serializers.SerializerMethodField()

    class Meta:
        model = salesRetailerTransactions
        # fields = ("transaction_amount", "mode_of_payment", "details","created","updated","retailer","retailerName")
        fields = '__all__'

    def get_sales_person(self, obj):
        return obj.retailer.user_id or obj.retailer.full_name
    def get_sales_person_name(self, obj):
        return obj.retailer.full_name or ''

    def get_retailerName(self, obj):
        return obj.retailer.enterprise_name or ''

    def get_retailer_id(self, obj):
        return obj.retailer.id or 0
    def get_distributor(self, obj):
        return UserSerializer(obj.distributor).data or {}


