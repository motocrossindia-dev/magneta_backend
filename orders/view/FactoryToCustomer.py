import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404

from orders.models import FactoryToCustomer
from products.models import Product
from orders.serializers.FactoryToCustomerSerializer import POSTfactoryToCustomerSerializer, GETfactoryToCustomerSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication, IsManagerPermission])
def factory_to_customer(request):
    user = request.user
    if request.method == 'POST':
        try:
            # Generate order number
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            last_order = FactoryToCustomer.objects.filter(order_date__range=(today_start, today_end)).order_by(
                '-order_number').first()

            if last_order:
                last_order_number = int(last_order.order_number[7:]) + 1
            else:
                last_order_number = 1

            if last_order_number > 9999:
                raise ValueError("Maximum orders exceeded for the day.")

            app_name = "F"
            order_number = f"{app_name}{str(today_start.year)[-2:]}{today_start.month:02d}{today_start.day:02d}"\
                            f"{last_order_number:04d}"

            main_order = request.data.get('main_order')
            ordered_products = request.data.get('ordered_products', [])

            for ordered_product_data in ordered_products:
                product = get_object_or_404(Product, pk=ordered_product_data.get('product_id'))
                order_data = {
                    'sold_by': user.pk,
                    'product_name': ordered_product_data.get('product_id'),
                    'order_date': main_order.get('order_date'),
                    'mode_of_payment': main_order.get('mode_of_payment'),
                    'payment_status': 'Paid',
                    'quantity': ordered_product_data.get('quantity'),
                    'mrp': product.mrp,
                    'amount': round((product.mrp * ordered_product_data.get('quantity')), 2)
                }
                if main_order.get('mode_of_payment') =='free sample' or main_order.get('mode_of_payment') =='stn':
                    order_data['mrp'] = 0
                    order_data['amount'] = 0
                serializer = POSTfactoryToCustomerSerializer(data=order_data)
                if serializer.is_valid():
                    serializer.save(order_number=order_number)
                elif serializer.errors:
                    logger.error("Error in orders: ", str(serializer.errors))
                    return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response(data={"msg": "Order created successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: factory_to_customer " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        try:
            orders = FactoryToCustomer.objects.all().order_by('-id')
            serializer = GETfactoryToCustomerSerializer(orders, many=True)
            return Response(data={"data": serializer.data})
        except Exception as e:
            logger.error("Exception: factory_to_customer " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in factory_to_customer: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
