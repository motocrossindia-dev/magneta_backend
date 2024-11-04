from rest_framework import serializers

from accounts.models import Role
from accounts.serializers.RolePermissionSerializer import GETrolePermissionSerializer


class POSTrolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class GETrolesSerializer(serializers.ModelSerializer):
    role_permissions = GETrolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        # fields = '__all__'
        fields = ['role', 'role_permissions']

    def get_permissions(self, obj):
        permissions = obj.role_permissions.all().values_list('permission', flat=True)
        return list(permissions)
