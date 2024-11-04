from rest_framework import serializers

from orders.models import PaymentTrack


class POSTPaymentTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTrack
        fields = ('main_order', 'status', 'updated_by', 'updator_contact', 'utrNo', 'cash', 'cheque')


class GETPaymentTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTrack
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance is not None:
            # Access attributes of instance only if it's not None
            # For example:
            representation['utrNo'] = instance.utrNo
            # Add more fields as needed

        return representation
