from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from accounts.models import UserBase

import logging

from accounts.serializers.DistributorBilledMainOrdersSerializer import GETdistributorBilledMainOrdersSerializer
from accounts.serializers.RetailerBilledMainOdersSerializer import GETretailerBilledMainOrdersSerializer
from distributors.models import RetailerMainOrders
from orders.models import MainOrders

logger = logging.getLogger("magneta_logger")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def user_bills(request, pk=None):
    if request.method == 'GET' and pk is not None:
        try:
            user = UserBase.objects.get(id=pk)
            if user.is_distributor:
                billed_main_orders = MainOrders.objects.filter(distributor=user)
                serializer = GETdistributorBilledMainOrdersSerializer(billed_main_orders, many=True)
                return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
            elif user.is_retailer:
                billed_main_orders = RetailerMainOrders.objects.filter(retailer=user)
                serializer = GETretailerBilledMainOrdersSerializer(billed_main_orders, many=True)
                return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
            else:
                logger.error("user_bills Data not found")
                return Response(data={"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Exception: user_bills " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("user_bills Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
