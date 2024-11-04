import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerOrDistributorPermission
from distributors.models import RetailerMainOrders
from distributors.serializers.RetailerMainOrderSerializer import GETretailerMainOrderSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsManagerOrDistributorPermission])
@authentication_classes([JWTAuthentication])
def retailer_main_orders(request, pk=None):
    user = request.user
    print("retailer_main_orders")

    if request.method == 'GET' and (user.is_distributor or user.is_manager) and pk is None:
        try:
            if user.is_distributor:
                retailer_main_order = RetailerMainOrders.objects.filter(distributor=user).order_by('-id')
            else:
                retailer_main_order = RetailerMainOrders.objects.all().order_by('-id')
            serializer = GETretailerMainOrderSerializer(retailer_main_order, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: retailer_main_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET' and user.is_manager and pk is not None:
        try:
            retailer_main_order = RetailerMainOrders.objects.get(id=pk)
            serializer = GETretailerMainOrderSerializer(retailer_main_order)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: retailer_main_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
