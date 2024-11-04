import re
from rest_framework import serializers

from inventory.models import Vendor, VendorContactPersons


class GETvendorsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = ['id', 'vendorFullname','enterpriseName']


class POSTvendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = '__all__'

    def validate(self, data):

        vendorGSTno = data.get('vendorGSTno', None)
        if vendorGSTno:
            vendorGSTno_pattern = re.compile(r'^\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z\d]$')
            if not vendorGSTno_pattern.match(vendorGSTno):
                raise serializers.ValidationError({"vendorGSTno": ["Invalid GST number format."]})

        return data


class POSTvendorContactPersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorContactPersons
        fields = '__all__'
        # fields = ['VCPname', 'phoneNumber']
