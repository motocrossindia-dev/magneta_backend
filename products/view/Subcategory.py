import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from products.models import Subcategory
from products.serializers.SucategorySerializer import GETSubcategorySerializer, POSTSubcategorySerializer, \
    PATCHSubcategorySerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'POST', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def subcategory(request, pk=None):
    if request.method == 'GET' and pk is None:
        try:
            subcategories = Subcategory.objects.all()
            serializer = GETSubcategorySerializer(subcategories, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: subcategory " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST' and pk is None:
        try:
            serializer = POSTSubcategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data={"msg": "Subcategory saved successfully"}, status=status.HTTP_201_CREATED)
            else:
                logger.error("Error in subcategory: ", str(serializer.errors))
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: subcategory " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH' and pk is not None:
        try:
            sbctgry = Subcategory.objects.get(id=pk)
            if sbctgry is None:
                logger.error("Subcategory not found")
                return Response(data={"msg": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                serializer = PATCHSubcategorySerializer(instance=sbctgry, data=request.data, partial=True,
                                                        context={'id': pk})
                if serializer.is_valid():
                    serializer.save()
                    return Response(data={"msg": "Subcategory updated successfully"}, status=status.HTTP_200_OK)
                else:
                    logger.error("Error in subcategory: ", str(serializer.errors))
                    return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: subcategory " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and pk is not None:
        try:
            sbctgry = Subcategory.objects.get(id=pk)
            if sbctgry is None:
                logger.error("Subcategory not found")
                return Response(data={"msg": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                sbctgry.delete()
                return Response(data={"msg": "Subcategory deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: subcategory " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# Get all subcategories based on category id
def get_subcategories_by_category_id(request, category_id=None):
    if request.method == 'GET' and category_id is not None:
        try:
            subcategories = Subcategory.objects.filter(category=category_id)
            serializer = GETSubcategorySerializer(subcategories, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: subcategory " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
