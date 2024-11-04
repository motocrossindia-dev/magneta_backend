import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from products.models import Category
from products.serializers.CategorySerializer import GETCategorySerializer, POSTCategorySerializer, \
    PATCHCategorySerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'POST', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
# @permission_classes([AllowAny])
def categories(request, pk=None):
    if request.method == 'GET' and pk is None:
        try:
            ctgrs = Category.objects.all()
            serializer = GETCategorySerializer(ctgrs, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: categories " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST' and pk is None:
        try:
            serializer = POSTCategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data={"msg": "Category created successfully", "data": serializer.data},
                                status=status.HTTP_201_CREATED)
            else:
                logger.error("Error in categories: ", str(serializer.errors))
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: categories " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH' and pk is not None:
        try:
            ctgr = Category.objects.get(id=pk)
            if ctgr is None:
                return Response(data={"msg": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                serializer = PATCHCategorySerializer(instance=ctgr, data=request.data, partial=True,
                                                     context={'id': pk})
                if serializer.is_valid():
                    serializer.save()
                    return Response(data={"msg": "Category updated successfully"}, status=status.HTTP_200_OK)
                else:
                    logger.error("Error in categories: ", str(serializer.errors))
                    return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: categories " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE' and pk is not None:
        try:
            ctgr = Category.objects.get(id=pk)
            if ctgr is None:
                logger.error("Error in categories: Category not found")
                return Response(data={"msg": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                ctgr.delete()
                return Response(data={"msg": "Category deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: categories " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in categories: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
