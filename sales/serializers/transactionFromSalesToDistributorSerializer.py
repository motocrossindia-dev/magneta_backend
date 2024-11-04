from rest_framework import serializers

from sales.models import transactionFromSalesToDistributor


class transactionFromSalesToDistributorSerializer(serializers.ModelSerializer):
    sales_person_name = serializers.SerializerMethodField()
    class Meta:
        model = transactionFromSalesToDistributor
        fields = '__all__'

    def get_sales_person_name(self, obj):
        return obj.sales_person.first_name
