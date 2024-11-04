from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from orders.models import GST
from orders.serializers.GstSerializer import GETgstSerializer, PATCHgstSerializer
import logging

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def gst(request):
    if request.method == 'GET':
        try:
            gst_ = GST.objects.filter(id=1)
            serializer = GETgstSerializer(gst_, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: gst " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
        try:
            gst_ = GST.objects.get(id=1)
            serializer = PATCHgstSerializer(gst_, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={"msg": "GST updated successfully"}, status=status.HTTP_200_OK)
            else:
                logger.error("Error in gst: ", str(serializer.errors))
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: gst " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in gst: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
