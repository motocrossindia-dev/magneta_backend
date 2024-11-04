import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission, IsManagerOrDistributorPermission, IsRetailerPermission, \
    IsManagerOrDistributorOrRetailerPermission
from distributors.models import DistributorStock
from products.models import Product, ProductImage, ProductSize, ProductFlavour, ProductSpecification
from products.serializers.ProductSerializer import (POSTProductSerializer, GETProductSerializer,
                                                    PATCHProductSerializer,
                                                    ProductImageSerializer, ProductSizeSerializer,
                                                    ProductFlavourSerializer, ProductSpecificationSerializer,
                                                    ChangeProductImageSerializer)
from products.serializers.StockSerializer import GETstockSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['POST', 'GET', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def products(request, pk=None, all=None):
    user = request.user
    if request.method == 'GET' and pk is None:
        try:
            if all and user.is_manager:
                prds = Product.objects.all()
            else:
                prds = Product.objects.filter(is_active=True)
            serializer = GETProductSerializer(prds, context={'request': request}, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: products " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET' and pk is not None:
        try:
            if all and user.is_manager:
                prds = Product.objects.filter(id=pk)
                serializer = GETProductSerializer(prds, context={'request': request}, many=True)
                return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(data={"Error": "Not Allowed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: products " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # elif request.method == 'POST' and pk is None:
    elif request.method == 'POST' and pk is None and request.user.is_manager:
        try:
            serializer = POSTProductSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                product = serializer.save()

                data = {"size_name": request.data.get('size_name'), "size_volume": request.data.get('size_volume'),
                        "product": product.id}

                serializer = ProductSizeSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                elif serializer.errors:
                    logger.error("Error in products: ", str(serializer.errors))
                    return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                data = {"flavour_name": request.data.get('flavour_name'), "product": product.id}
                serializer = ProductFlavourSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                elif serializer.errors:
                    logger.error("Error in products: ", str(serializer.errors))
                    return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                return Response(data={"msg": "Products saved successfully"}, status=status.HTTP_201_CREATED)
            else:
                logger.error("Error in products: ", str(serializer.errors))
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: products " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # elif request.method == 'PATCH' and pk is not None:
    elif request.method == 'PATCH' and pk is not None and request.user.is_manager:
        try:
            prd = Product.objects.get(id=pk)
            if prd is None:
                return Response(data={"msg": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                serializer = PATCHProductSerializer(instance=prd, data=request.data, partial=True, context={'id': pk})
                if serializer.is_valid():
                    serializer.save()

                    data = {"size_name": request.data.get('size_name'), "size_volume": request.data.get('size_volume')}

                    product_size = ProductSize.objects.filter(product=prd).first()
                    serializer = ProductSizeSerializer(instance=product_size, data=data, partial=True)

                    if serializer.is_valid():
                        serializer.save()

                    elif serializer.errors:
                        logger.error("Error in products: ", str(serializer.errors))
                        return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    data = {"flavour_name": request.data.get('flavour_name')}

                    product_flavour = ProductFlavour.objects.filter(product=prd).first()
                    serializer = ProductFlavourSerializer(instance=product_flavour, data=data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                    elif serializer.errors:
                        logger.error("Error in products: ", str(serializer.errors))
                        return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    product_image_data = request.FILES.get('image')
                    if product_image_data:
                        serializer = ChangeProductImageSerializer(instance=prd, data={'image': product_image_data},
                                                                  partial=True)
                        if serializer.is_valid():
                            serializer.save()
                        elif serializer.errors:
                            return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    return Response(data={"msg": "Product updated successfully"}, status=status.HTTP_200_OK)
                else:
                    logger.error("Error in products: ", str(serializer.errors))
                    return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: products " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # elif request.method == 'DELETE' and pk is not None and request.user.is_manager:
    elif request.method == 'DELETE' and pk is not None:
        try:
            prd = Product.objects.get(id=pk)
            if prd is None:
                logger.error("Error in products: Product not found")
                return Response(data={"msg": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                prd.delete()
                return Response(data={"msg": "Product deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: products " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in products: Not authorized or Invalid request")
        return Response(data={"error": "Not authorized or Invalid request"}, status=status.HTTP_404_NOT_FOUND)
