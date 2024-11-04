import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from inventory.models import Vendor, Type
from inventory.serializers.TypeSerializer import GETtypeSerializer
from inventory.serializers.VendorSerializer import POSTvendorSerializer, POSTvendorContactPersonSerializer, \
    GETvendorsSerializer

from accounts.CustomPermissions import IsManagerPermission, IsStoreManagerPermission

logger = logging.getLogger("magneta_logger")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStoreManagerPermission])
@authentication_classes([JWTAuthentication])
def vendor(request):
    if request.method == "GET":
        try:
            vendors = Vendor.objects.all()
            serializer = GETvendorsSerializer(vendors, many=True)

            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: vendor " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "POST":
        try:
            serializer = POSTvendorSerializer(data=request.data.get('Vendor'))
            if serializer.is_valid():
                vd = serializer.save()
                for vendor_contact_person_data in request.data.get('VendorContactPersons'):
                    vendor_contact_person_data['vendor'] = int(vd.id)

                    vendor_contact_person_serializer = POSTvendorContactPersonSerializer(
                        data=vendor_contact_person_data)
                    if vendor_contact_person_serializer.is_valid():
                        vendor_contact_person_serializer.save()
                    elif vendor_contact_person_serializer.errors:
                        logger.error("Error in vendor: ", str(vendor_contact_person_serializer.errors))
                        return Response(data={"error": vendor_contact_person_serializer.errors},
                                        status=status.HTTP_400_BAD_REQUEST)
                return Response(data={"data": "vendor added successfully."}, status=status.HTTP_200_OK)
            elif serializer.errors:
                logger.error("Error in vendor: ", str(serializer.errors))
                return Response(data={"error": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: vendor " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
