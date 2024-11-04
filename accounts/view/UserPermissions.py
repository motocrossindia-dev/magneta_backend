from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from accounts.models import RolesPermission, Role
from accounts.serializers.RolePermissionSerializer import GETrolePermissionSerializer


def user_permissions(user_id):
    try:
        get_user = get_user_model().objects.get(id=user_id)

        if get_user:
            try:
                user_roles = RolesPermission.objects.filter(user=user_id)
            except Exception as e:
                if user_roles.is_manager:
                    return "manager", []
                else:
                    return None, None
            if user_roles:
                serializer = GETrolePermissionSerializer(user_roles, many=True)
                serialized_data = serializer.data
                try:
                    if not get_user.is_manager:
                        role_permissions_formatted = [item['permission'] for item in serialized_data]
                        role = get_user.role.role
                    else:
                        role_permissions_formatted =[]
                        role = "manager"

                except Exception as e:
                    role_permissions_formatted = None
                    if get_user.role.role:
                        role = get_user.role.role
                    else:
                        role = None
                return role, role_permissions_formatted
            else:
                if get_user.is_manager:
                    return "manager", []
                else:
                    return get_user.role.role or None, None
        return None, None
    except:
        return None, None


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def update_user_permissions(request):
    if request.method == 'POST':
        user_id = request.data.get('user', None)
        role = request.data.get('role', None)
        permission = request.data.get('permission', None)
        user = get_user_model().objects.get(id=user_id)
        if user:
            if permission:
                role = user.role if role is None else role
                role, created = RolesPermission.objects.get_or_create(user=user, role=role, permission=permission)
                if created:
                    return Response(data={'success': 'Permission added successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(data={'error': 'Permission already exists for this user'},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response(data={'error': 'role and permission are required'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def get_all_user_permissions():
    try:
        role_permissions = RolesPermission.objects.all()
        serializer = GETrolePermissionSerializer(role_permissions, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_user_permissions(request, user_id):
    try:
        user = get_user_model().objects.get(id=user_id)
        role_permissions = RolesPermission.objects.filter(user=user).values_list("permission", flat=True)
        role_permissions_with_id = RolesPermission.objects.filter(user=user).values("id", "permission")
        return Response(data={"permissions": role_permissions, "permission_id": role_permissions_with_id},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def update_user_permissions(request):
    try:
        if request.method == 'POST':
            user_id = request.data.get('id', None)
            role = request.data.get('role', None)
            permissions = request.data.get('permissions', [])
            user = get_user_model().objects.get(id=user_id)
            if user:
                if permissions:
                    created_permissions = []
                    for permission in permissions:
                        # role = user.role if role is None else role
                        role_name = user.role.role if role is None else role
                        role = Role.objects.get(role=role_name)
                        role_obj, created = RolesPermission.objects.get_or_create(user=user, role=role,
                                                                                  permission=permission)
                        if created:
                            created_permissions.append(permission)
                    # Prepare response data
                    if created_permissions:
                        created_permissions_str = ', '.join(created_permissions)
                        return Response(data={'success': f'Permissions created for: {created_permissions_str}'},
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response(data={'error': 'No permissions created'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(data={'error': 'permissions list is empty'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes(
    [IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def delete_user_permission(request, permission_id):
    try:
        permission = get_object_or_404(RolesPermission, id=permission_id)
        user = permission.user
        permission.delete()

        other_permissions = RolesPermission.objects.filter(user=user).exclude(id=permission_id).values_list(
            "permission", flat=True)

        return Response(data={'success': 'Permission deleted successfully',
                              'other_permissions': other_permissions}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
