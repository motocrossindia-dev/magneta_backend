from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserBase


class SalesLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def __init__(self, *args, **kwargs):
        self.login_from = kwargs.pop('login_from', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        print(data,"data")
        email = data.get('email')
        password = data.get('password')
        login_from = self.login_from
        print(login_from,"login_from")

        user = UserBase.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"email": ["User with this email does not exist."]})
        elif len(data.get('password')) < 3:
            raise serializers.ValidationError({"password": ["Password should be at least 3 characters long."]})
        elif not user.check_password(password):
            raise serializers.ValidationError({"password": ["Invalid password."]})
        elif not user.is_active:
            raise serializers.ValidationError("Account activation failed. Please contact factory.")
        elif user.is_distributor is False:
            raise serializers.ValidationError("Not a distributor.")
        elif login_from == 'phone':
            if user.role.role != "sales":
                raise serializers.ValidationError("Not a distributor sales personnel.")
        elif login_from == 'web':
            if user.role.role == "sales":
                raise serializers.ValidationError("Not a distributor. please login to mobile app.")

        data['user'] = user
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        representation.pop('email', None)

        user = instance['user']
        representation['id'] = user.id
        representation['profile_picture'] = user.profile_picture.url if user.profile_picture else None
        representation['first_name'] = user.first_name
        representation['last_name'] = user.last_name if user.last_name else None
        representation['default_password'] = user.default_password
        representation['phone_number'] = user.phone_number if user.phone_number else None

        if user.is_manager:
            representation['is_manager'] = True
        if user.is_distributor:
            representation['is_distributor'] = True
        if user.is_retailer:
            representation['is_retailer'] = True

        refresh = RefreshToken.for_user(user)

        representation['token'] = {"refresh": str(refresh), "access": str(refresh.access_token)}

        return representation
