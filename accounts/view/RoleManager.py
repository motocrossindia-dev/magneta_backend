from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from accounts.models import Role


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def create_role(request):
    if request.method == 'POST':

        role_name = request.data.get('role', None)
        if role_name:
            if Role.objects.filter(role=role_name).exists():
                return JsonResponse({'error': 'Role already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            new_role = Role.objects.create(role=role_name)
            return JsonResponse({'success': 'Successfully created new role', 'id': new_role.id, 'role': new_role.role}, status=201)
        else:
            return JsonResponse({'error': 'Role name is required'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def update_role(request, role_id):
    if request.method == 'POST':
        role_name = request.data.get('role', None)
        delete_role = request.data.get('delete', None)
        if delete_role:
            try:
                role_instance = Role.objects.get(id=role_id)
                role_instance.delete()
                return JsonResponse({'success': 'Successfully deleted role'}, status=200)
            except Role.DoesNotExist:
                return JsonResponse({'error': 'Role not found'}, status=404)
        elif role_name:
            try:
                role_instance = Role.objects.get(id=role_id)
                role_instance.role = role_name
                role_instance.save()
                return JsonResponse({'success': 'Successfully updated role','id': role_instance.id, 'role': role_instance.role}, status=200)
            except Role.DoesNotExist:
                return JsonResponse({'error': 'Role not found'}, status=404)
        else:
            return JsonResponse({'error': 'Role name is required'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def get_roles(request):
    if request.method == 'GET':
        roles = Role.objects.all()
        roles_list = [{'id': role.id, 'role': role.role} for role in roles]
        return JsonResponse(roles_list, safe=False, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

