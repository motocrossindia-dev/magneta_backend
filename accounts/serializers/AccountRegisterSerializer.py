from rest_framework import serializers

from accounts.models import UserBase
import re


class POSTaccountRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = ['id',
                  'is_active',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'enterprise_name',
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
                  'is_active',
                  'role'
                  ]
        extra_kwargs = {
            'password': {'write_only': True},
            # 'email': {'required': True}
        }
        depth=1

    # def get_profile_picture_url(self, obj):
    #     request = self.context.get('request')
    #     if obj.profile_picture:
    #         return request.build_absolute_uri(obj.profile_picture.url)
    #     return None

    def validate(self, data):
        phone_number = data.get('phone_number', None)
        if phone_number:
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

        gst = data.get('gst', None)
        if gst:
            gst_pattern = re.compile(r'^\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z\d]$')
            if not gst_pattern.match(gst):
                raise serializers.ValidationError({"gst": ["Invalid GST number format."]})

        pan = data.get('pan', None)
        if pan:
            pan_pattern = re.compile(r'^[A-Z]{5}\d{4}[A-Z]$')
            if not pan_pattern.match(pan):
                raise serializers.ValidationError({"pan": ["Invalid PAN number format."]})

        aadhar = data.get('aadhar', None)
        if aadhar:
            if not aadhar.isdigit():
                raise serializers.ValidationError({"aadhar": ["Aadhar number should only contain digits."]})
            if len(aadhar) != 12:
                raise serializers.ValidationError({"aadhar": ["Aadhar number should be exactly 12 digits long."]})

        return data

    def create(self, validated_data):
        user = UserBase.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data


class PATCHaccountRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        exclude = ['profile_picture']

    def validate(self, data):
        phone_number = data.get('phone_number', None)
        if phone_number:
            if not phone_number.isdigit():
                raise serializers.ValidationError({"phone_number": ["Phone number should only contain digits."]})
            if len(phone_number) != 10:
                raise serializers.ValidationError({"phone_number": ["Phone number should be exactly 10 digits long."]})
            if phone_number[0] not in ['6', '7', '8', '9']:
                raise serializers.ValidationError({"phone_number": ["Phone number should start with 6, 7, 8, or 9."]})

        if data.get('password') != self.context.get('request').data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": ["Passwords do not match."]})

        gst = data.get('gst', None)
        if gst:
            gst_pattern = re.compile(r'^\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z\d]$')
            if not gst_pattern.match(gst):
                raise serializers.ValidationError({"gst": ["Invalid GST number format."]})

        pan = data.get('pan', None)
        if pan:
            pan_pattern = re.compile(r'^[A-Z]{5}\d{4}[A-Z]$')
            if not pan_pattern.match(pan):
                raise serializers.ValidationError({"pan": ["Invalid PAN number format."]})

        aadhar = data.get('aadhar', None)
        if aadhar:
            if not aadhar.isdigit():
                raise serializers.ValidationError({"aadhar": ["Aadhar number should only contain digits."]})
            if len(aadhar) != 12:
                raise serializers.ValidationError({"aadhar": ["Aadhar number should be exactly 12 digits long."]})

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data


class ChangeProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = ['profile_picture']
