from rest_framework import serializers
from advertisements.models import Banner


class GETbannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['image']
