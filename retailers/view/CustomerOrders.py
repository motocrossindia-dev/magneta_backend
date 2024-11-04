import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsRetailerPermission
from products.models import Product
from retailers.models import CustomerOrders
from retailers.serializers.CustomerMainOrderSerializer import POSTcustomerMainOrdersSerializer
from retailers.serializers.CustomerOrderSerializer import POSTcustomerOrderSerializer, GETcustomerOrdersSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsRetailerPermission])
@authentication_classes([JWTAuthentication])
def customer_orders(request, pk=None):
    user = request.user
    if request.method == 'GET' and pk is not None:
        try:
            customer_order = CustomerOrders.objects.filter(customerMainOrder=pk)
            serializer = GETcustomerOrdersSerializer(customer_order, many=True)

            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: customer_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST' and pk is None:
        try:
            ordered_products = request.data.get('ordered_products', [])
            main_order = request.data.get('main_order', {})
            if main_order['customerFullName'] == '':
                main_order['customerFullName'] = 'Default Customer'
            if main_order['customerPhoneNumber'] == '':
                main_order['customerPhoneNumber'] = '0000000000'
            main_order_serializer = POSTcustomerMainOrdersSerializer(data=main_order,
                                                                     context={'request': ordered_products})
            if main_order_serializer.is_valid():
                main_order = main_order_serializer.save(retailer=user)
                for ordered_product_data in ordered_products:
                    product_id = ordered_product_data.get('productId')
                    product = get_object_or_404(Product, pk=product_id)

                    ordered_product_data['customerMainOrder'] = main_order.pk
                    ordered_product_data['productName'] = product.product_name

                    ordered_product_data['mrp'] = product.mrp
                    ordered_product_data['sum'] = round((ordered_product_data['quantity'] * product.mrp), 2)

                    ordered_product = POSTcustomerOrderSerializer(data=ordered_product_data)
                    if ordered_product.is_valid():
                        ordered_product = ordered_product.save()
                    else:
                        logger.error("Error in customer_orders: ", str(ordered_product.errors))
                        return Response(data={"error": ordered_product.errors},
                                        status=status.HTTP_400_BAD_REQUEST)

                ordered_products = CustomerOrders.objects.filter(customerMainOrder=main_order).all()
                main_order.grandTotal = round((sum(ordered_product.sum for ordered_product in ordered_products)),
                                              2)
                main_order.save()

                return Response(data={"data": "Customer Order created successfully."}, status=status.HTTP_200_OK)
            else:
                logger.error("Error in customer_orders: " + str(main_order_serializer.errors))
                return Response(data={"error": main_order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error("Exception: customer_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)

