import logging
from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from orders.serializers.DashboardSerializer import GETdashboardSerializer
from orders.models import MainOrders

logger = logging.getLogger("magneta_logger")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def dashboard(request):
    if request.method == 'GET':
        try:
            total_grand_total = \
                MainOrders.objects.filter(status='Delivered').aggregate(
                    total_grand_total=Sum('grand_total'))[
                    'total_grand_total'] or 0.0
            total_delivered_orders = MainOrders.objects.filter(status='Delivered').count()

            # Serialize the data
            serializer = GETdashboardSerializer({
                'total_grand_total': total_grand_total,
                'total_delivered_orders': total_delivered_orders
            })

            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in dashboard: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
