from rest_framework import serializers

from accounts.models import UserBase


class retailerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = ['id', 'user_id', 'first_name', 'phone_number', 'pan', 'gst', 'Address', 'email', 'pincode',
                  'enterprise_name']
