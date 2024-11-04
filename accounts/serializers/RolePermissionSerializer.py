from rest_framework import serializers

from accounts.models import RolesPermission


class POSTrolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesPermission
        fields = '__all__'


class GETrolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolesPermission
        fields = ['role', 'permission']
        depth = 1
