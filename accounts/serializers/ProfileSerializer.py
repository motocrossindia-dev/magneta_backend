from django.utils.dateparse import parse_date
from rest_framework import serializers

from accounts.models import UserBase


class GETUserProfileSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(format='%d-%m-%Y')

    class Meta:
        model = UserBase
        fields = ('profile_picture', 'first_name', 'last_name', 'date_of_birth', 'email', 'phone_number',
                  'emergency_phone_number', 'aadhar', 'pan', 'gst', 'city', 'is_manager', 'is_distributor',
                  'is_retailer', 'id', 'Address', 'state', 'role')
        depth = 1

    # def validate(self, data):
    #     # Validate date_of_birth field
    #     date_of_birth = data.get('date_of_birth', None)
    #     if date_of_birth:
    #         try:
    #             # Attempt to parse the date in 'YYYY-MM-DD' format
    #             parsed_date = parse_date(date_of_birth)
    #             print('---------------------------------------------', parsed_date)
    #             if parsed_date is None:
    #                 raise serializers.ValidationError(
    #                     {"date_of_birth": ["Invalid date format. Use 'YYYY-MM-DD' format."]})
    #         except Exception as e:
    #             raise serializers.ValidationError({"date_of_birth": ["Invalid date format. Use 'YYYY-MM-DD' format."
    #                                                                  + str(e)]})
    #
    #     # Other validation code for phone_number, password, etc.
    #     return data

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     date_of_birth = instance.date_of_birth.strftime("%d-%m-%Y")
    #     representation['date_of_birth'] = date_of_birth
    #     return representation
