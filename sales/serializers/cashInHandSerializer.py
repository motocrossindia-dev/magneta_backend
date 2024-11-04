from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from sales.models import salesPersonCashInHand, salesRetailerTransactions


class GetCashInHandSerializer(serializers.ModelSerializer):
    sales_person_name = serializers.SerializerMethodField()
    sales_person_id = serializers.SerializerMethodField()

    class Meta:
        model = salesPersonCashInHand
        fields = (
        'id', 'sales_person_id', 'sales_person_name', 'cash_in_hand', 'amount_transferred_to_distributer', 'total')

    def get_sales_person_name(self, obj):
        return obj.sales_person.first_name

    def get_sales_person_id(self, obj):
        return obj.sales_person.id


class GetCashInHandWithTodaysCollectionSerializer(serializers.ModelSerializer):
    sales_person_name = serializers.SerializerMethodField()
    sales_person_id = serializers.SerializerMethodField()
    todays_transaction_amount = serializers.SerializerMethodField()
    todays_cash_collection = serializers.SerializerMethodField()

    class Meta:
        model = salesPersonCashInHand
        fields = ('id', 'sales_person_id',
                  'sales_person_name', 'cash_in_hand',
                  'amount_transferred_to_distributer',
                  'todays_transaction_amount', 'todays_cash_collection', 'total')

    def get_sales_person_name(self, obj):
        return obj.sales_person.first_name

    def get_sales_person_id(self, obj):
        return obj.sales_person.id

    def get_todays_cash_collection(self, obj):
        today = timezone.now().date()
        todays_cash_transactions = salesRetailerTransactions.objects.filter(sales_person=obj.sales_person,
                                                                            created__date=today,
                                                                            mode_of_payment='cash')
        todays_cash_collection = todays_cash_transactions.aggregate(total=Sum('transaction_amount'))['total'] or 0.0
        return todays_cash_collection

    def get_todays_transaction_amount(self, obj):
        today = timezone.now().date()
        todays_transactions = salesRetailerTransactions.objects.filter(sales_person=obj.sales_person,
                                                                       created__date=today,
                                                                       )
        todays_collection = todays_transactions.aggregate(total=Sum('transaction_amount'))['total'] or 0.0
        return todays_collection
