from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserBase


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = UserBase.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": ["User with this email does not exist."]})
        elif len(data.get('password')) < 3:
            raise serializers.ValidationError({"password": ["Password should be at least 3 characters long."]})
        elif not user.check_password(password):
            raise serializers.ValidationError({"password": ["Invalid password."]})
        elif not user.is_active:
            raise serializers.ValidationError("Account activation failed. Please contact factory.")

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
        # if user.groups:
        #     role = user.groups
        #     representation['role'] = role.role  # Serialize the role attribute of the Role object
        #
        #     # Fetch permissions associated with the role
        #     permissions = RolesPermission.objects.filter(role=role)
        #     permission_list = [permission.permission for permission in permissions]
        #     representation['permissions'] = permission_list
        # else:
        #     representation['role'] = None
        #     representation['permissions'] = []

        if user.is_manager:
            representation['is_manager'] = True
        if user.is_distributor:
            representation['is_distributor'] = True
        if user.is_retailer:
            representation['is_retailer'] = True

        refresh = RefreshToken.for_user(user)

        representation['token'] = {"refresh": str(refresh), "access": str(refresh.access_token)}

        return representation


