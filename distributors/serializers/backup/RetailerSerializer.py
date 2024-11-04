from rest_framework import serializers

from accounts.models import UserBase


class POSTretailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = ['id',
                  'is_active',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'emergency_phone_number',
                  'email',
                  'Address',
                  'state',
                  'city',
                  'pincode',
                  'password',
                  'otp',
                  'date_of_birth',
                  'aadhar',
                  'pan',
                  'gst',
                  'is_retailer',
                  'is_distributor',
                  'is_manager',
                  'profile_picture',
                  ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    # def get_profile_picture_url(self, obj):
    #     request = self.context.get('request')
    #     if obj.profile_picture:
    #         return request.build_absolute_uri(obj.profile_picture.url)
    #     return None

    def validate(self, data):
        phone_number = data.get('phone_number', None)
        if not phone_number.isdigit():
            raise serializers.ValidationError({"phone_number": ["Phone number should only contain digits."]})
        if len(phone_number) != 10:
            raise serializers.ValidationError({"phone_number": ["Phone number should be exactly 10 digits long."]})
        if phone_number[0] not in ['6', '7', '8', '9']:
            raise serializers.ValidationError({"phone_number": ["Phone number should start with 6, 7, 8, or 9."]})

        if data.get('password') != self.context.get('request').data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": ["Passwords do not match."]})

        if len(data.get('password')) < 3:
            raise serializers.ValidationError({"password": ["Password should be at least 3 characters long."]})

        return data

    def create(self, validated_data):
        user = UserBase.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data


class GETretailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = ['id', 'user_id', 'first_name', 'phone_number', 'pan', 'gst', 'Address','email','pincode','enterprise_name']
