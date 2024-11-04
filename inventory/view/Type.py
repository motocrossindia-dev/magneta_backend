import logging
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsStoreManagerPermission
from inventory.models import Type
from inventory.serializers.TypeSerializer import POSTtypeSerializer

logger = logging.getLogger("magneta_logger")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStoreManagerPermission])
@authentication_classes([JWTAuthentication])
def types(request):
    if request.method == "GET":
        try:
            pass
        except Exception as e:
            logger.error("Exception: vendor " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "POST":
        serializer = POSTtypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"data": "Type created Successfully"}, status=status.HTTP_200_OK)
        elif serializer.errors:
            logger.error("Error in types: ", str(serializer.errors))
            return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)