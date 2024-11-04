import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsStoreManagerPermission
from inventory.models import Vendor, Material, Type, SubType
from inventory.serializers.MaterialSerializer import GETmaterialSerializer, POSTMaterialSerializer
from inventory.serializers.SubTypeSerializer import GETsubTypeSerializer
from inventory.serializers.TypeSerializer import GETtypeSerializer
from inventory.serializers.VendorSerializer import GETvendorsSerializer

logger = logging.getLogger("magneta_logger")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStoreManagerPermission])
@authentication_classes([JWTAuthentication])
def material(request):
    if request.method == "GET":
        try:
            materials = Material.objects.all()
            material_serializer = GETmaterialSerializer(materials, many=True)

            # All types
            types = Type.objects.all()
            type_serializer = GETtypeSerializer(types, many=True)

            subtypes = SubType.objects.all()
            subtype_serializer = GETsubTypeSerializer(subtypes, many=True)

            # All vendors
            vendors = Vendor.objects.all()
            serializer2 = GETvendorsSerializer(vendors, many=True)
            return Response(data={"data": material_serializer.data,
                                  "data1": type_serializer.data,
                                  "data2": serializer2.data,
                                  "subType": subtype_serializer.data
                                  }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: vendor " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "POST":
        try:
            print(request.data, "request.data")
            serializer = POSTMaterialSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({"success": "Material added successfully", "data": serializer.data},
                                status=status.HTTP_200_OK)
            print(serializer.errors)
            return Response({"error": "Error while adding material", "data": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in add_material: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
