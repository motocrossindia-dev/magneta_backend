from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerOrDistributorPermission, IsManagerPermission
from orders.models import MainOrders
from orders.serializers.MainOrdersSerializer import GETmainOrdersSerializer

import logging

logger = logging.getLogger("magneta_logger")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def main_orders(request, pk=None):
    if request.method == 'GET' and pk is None:
        try:
            main_order = MainOrders.objects.all().order_by('-id')
            serializer = GETmainOrdersSerializer(main_order, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: main_orders " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET' and pk is not None:
        try:
            distributor_orders = MainOrders.objects.filter(distributor_id=pk)
            serializer = GETmainOrdersSerializer(distributor_orders, many=True)
            # calculate sum of pending amount based on distributor and consider status Accepted and Verifying Payment
            pending = 0
            for order in distributor_orders:
                if order.status == "Accepted" or order.payment_status == "Verifying Payment":
                    pending += order.grand_total
            return Response(data={"data": serializer.data, "pending": pending}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: main_orders " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in main_orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def search_main_orders(request):
    if request.method == 'POST':
        try:
            filter_query = Q()

            if request.data.get('status') != '' and request.data.get('status') is not None:
                filter_query &= Q(status=request.data.get('status'))

            name = request.data.get('name')
            if name != '':
                try:
                    first_name, _ = request.data.get('name').rsplit('_', 1)
                    filter_query &= Q(distributor__first_name=first_name)
                except:
                    pass

            if request.data.get('mode_of_payment') != '':
                filter_query &= Q(mode_of_payment=request.data.get('mode_of_payment'))

            date_from = request.data.get('start_date')
            date_to = request.data.get('end_date')
            if date_from:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')

                filter_query &= Q(order_date__gte=date_from)

            if date_to:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                filter_query &= Q(order_date__lte=date_to)

            filtered_data = MainOrders.objects.filter(filter_query)

            if not filtered_data:
                return Response(data={"data": ["no data found"]}, status=status.HTTP_200_OK)
            serializer = GETmainOrdersSerializer(filtered_data, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: search_main_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("search_main_orders Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
