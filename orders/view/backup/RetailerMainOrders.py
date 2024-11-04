import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsDistributorPermission
from orders.models import RetailerMainOrders
from orders.serializers.RetailerMainOrderstSerializer import GETretailerMainOrderssSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDistributorPermission])
@authentication_classes([JWTAuthentication])
def retailer_main_orders(request, pk=None):
    if request.method == 'GET' and pk is None:
        try:
            retailer_main_order = RetailerMainOrders.objects.all().order_by('-id')
            serializer = GETretailerMainOrderssSerializer(retailer_main_order, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: retailer_main_orders " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET' and pk is not None:
        try:
            retailer_orders = RetailerMainOrders.objects.filter(distributor=pk)
            serializer = GETretailerMainOrderssSerializer(retailer_orders, many=True)
            return Response(data={"data": serializer.data, "pending": "50000"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: retailer_main_orders " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in retailer_main_orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
