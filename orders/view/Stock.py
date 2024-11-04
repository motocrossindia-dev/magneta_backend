import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from accounts.models import UserBase
from distributors.models import DistributorStock
from orders.serializers.DistributorStockSerializer import GETdistributorStockSerializer

logger = logging.getLogger("magneta_logger")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def stock(request, pk=None):
    if request.method == 'GET' and pk is not None:
        try:
            person = UserBase.objects.get(id=pk)
            if person.is_distributor:
                stock_data = DistributorStock.objects.filter(distributor_id=person)
                serializer = GETdistributorStockSerializer(stock_data, many=True)
                return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(data={"data": "Data not found"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: gst " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    else:
        logger.error("Error in gst: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
