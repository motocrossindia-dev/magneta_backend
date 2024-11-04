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
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def retailer_main_orders(request, pk=None):
    user = request.user
    if request.method == 'GET' and pk is None:
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

    elif request.method == 'GET' and pk is not None:
        print(pk, "pk")
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_sales_person_orders(request, pk=None):
    user = request.user
    if request.method == 'GET':
        try:
            if user.is_distributor:
                retailer_main_order = RetailerMainOrders.objects.filter(distributor__id=pk).order_by('-id')
            else:
                retailer_main_order = RetailerMainOrders.objects.all().order_by('-id')
            serializer = GETretailerMainOrderSerializer(retailer_main_order, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: retailer_main_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
