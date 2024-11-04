from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from accounts.models import Otp, UserBase


class CheckOtpSerializer(serializers.Serializer):

    def validate(self, data):
        user = UserBase.objects.filter(email=self.context.get('request').get('email')).first()
        user_otp = self.context.get('request').get('otp')
        if user.otp != user_otp:
            raise serializers.ValidationError({"otp": ["Invalid OTP."]})
        if user_otp is None:
            raise serializers.ValidationError({"otp": ["OTP is required."]})
        else:
            user.password = make_password(self.context.get('request').get('password'))
            if user.default_password:
                user.default_password = False
            user.otp = None
            user.save()
            data['user'] = user
            return data
