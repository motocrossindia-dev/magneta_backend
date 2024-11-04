from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from accounts.models import UserBase, Otp


class POSTsetResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()

    def validate(self, data):
        password = data.get('password')
        user = UserBase.objects.filter(email=self.context.get('request').get('email')).first()
        if not user:
            raise serializers.ValidationError({"email": ["User with this email does not exist."]})
        elif password != self.context.get('request').get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": ["Passwords do not match."]})
        elif len(data.get('password')) < 3:
            raise serializers.ValidationError({"password": ["Password should be at least 3 characters long."]})
        elif not user.is_active:
            raise serializers.ValidationError("User account deactivated of this account.")

        user_otp = self.context.get('request').get('otp')
        db_otp = Otp.objects.filter(user=user, otp=user_otp).first()
        if not db_otp and user_otp != db_otp.otp:
            raise serializers.ValidationError({"otp": ["Invalid OTP."]})

        else:
            user.password = make_password(password)
            user.save()
            data['user'] = user
            return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        representation.pop('email', None)

        user = instance['user']
        representation['profile_picture'] = user.profile_picture.url if user.profile_picture else None
        representation['first_name'] = user.first_name
        representation['last_name'] = user.last_name if user.last_name else None
        return representation
