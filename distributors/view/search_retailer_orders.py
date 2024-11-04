from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
import logging

from distributors.models import RetailerMainOrders

logger = logging.getLogger("magneta_logger")

from distributors.serializers.RetailerMainOrderSerializer import GETretailerMainOrderSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def search_retailer_orders(request):
    if request.method == 'POST':
        try:
            filter_query = Q()
            date_from = request.data.get('start_date')
            date_to = request.data.get('end_date')
            mode_of_payment = request.data.get('mode_of_payment')
            name = request.data.get('name')

            if mode_of_payment != '':
                filter_query &= Q(mode_of_payment=request.data.get('mode_of_payment'))

            if name != '':
                first_name, _ = request.data.get('name').rsplit('_', 1)
                filter_query &= Q(retailer__first_name=first_name)

            if date_from:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                filter_query &= Q(order_date__gte=date_from)

            if date_to:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                filter_query &= Q(order_date__lte=date_to)

            filtered_data = RetailerMainOrders.objects.filter(filter_query)[:100]

            if not filtered_data:
                return Response(data={"data": ["no data found"]}, status=status.HTTP_200_OK)
            serializer = GETretailerMainOrderSerializer(filtered_data, many=True)
            # print( serializer.data," serializer.data")
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: search_main_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("search_main_orders Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
