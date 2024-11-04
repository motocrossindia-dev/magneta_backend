from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsDistributorPermission, IsManagerPermission
from accounts.models import UserBase


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated, IsDistributorPermission])
@authentication_classes([JWTAuthentication])
def delete_account(request):
    if request.method == "POST":
        try:
            user = UserBase.objects.get(id=request.user.id)
            user.is_active = False
            user.save()
            return Response(data={"msg": "Account Deleted Successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            # logger.error("Exception: distributor_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def delete_profile_picture(request, pk=None):
    if request.method == 'POST':
        try:
            user = UserBase.objects.get(id=pk)
            user.profile_picture = "profile_image/default_profile.png"
            user.save()
            return Response(data={"data": "Profile picture deleted successfully."})
        except Exception as e:
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
