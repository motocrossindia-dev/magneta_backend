import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsRetailerPermission
from retailers.models import CustomerMainOrders
from retailers.serializers.CustomerMainOrderSerializer import GETcustomerMainOrderSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsRetailerPermission])
@authentication_classes([JWTAuthentication])
def customer_main_order(request, pk=None):
    user = request.user

    if request.method == 'GET' and pk is None:
        try:
            customer_main_orders = CustomerMainOrders.objects.filter(retailer=user).order_by('-id')
            serializer = GETcustomerMainOrderSerializer(customer_main_orders, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: retailer_main_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
