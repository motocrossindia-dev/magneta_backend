import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsDistributorPermission
from accounts.models import UserBase
from distributors.serializers.RetailerSerializer import GETretailerSerializer

logger = logging.getLogger("magneta_logger")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsDistributorPermission])
@authentication_classes([JWTAuthentication])
def retailers(request):
    if request.method == "GET":
        try:
            retailer = UserBase.objects.filter(is_retailer=True)
            serializer = GETretailerSerializer(retailer, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: distributor_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
