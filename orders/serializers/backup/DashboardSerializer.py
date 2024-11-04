from rest_framework import serializers


class GETdashboardSerializer(serializers.Serializer):
    total_grand_total = serializers.FloatField()
    total_delivered_orders = serializers.IntegerField()
