import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from distributors.models import RetailerMainOrders, RetailerOrders, DistributorStock
from distributors.serializers.RetailerOrderSerializer import GETretailerOrderSerializer
from orders.models import GST
from sales.models import salesPerson_orders, distributor_sales

logger = logging.getLogger("magneta_logger")


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def orders(request, pk=None):
    # user = request.user
    # gst = GST.objects.get(id=1)
    print("in sales/orders")

    if request.method == 'GET' and pk is not None:
        try:
            main_order = get_object_or_404(RetailerMainOrders, pk=pk)
            order_details = RetailerOrders.objects.filter(retailer_main_order=pk)
            serializer = GETretailerOrderSerializer(order_details, many=True)

            return Response(data={"data": serializer.data, "order_number": main_order.order_number},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: distributor_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def order_from_sales_person(main_order, sales_person):
    def reduce_stock(main_order):
        try:
            sold_products = RetailerOrders.objects.filter(retailer_main_order=main_order)

            for sold_product in sold_products:
                # Try to retrieve existing DistributorStock object
                try:
                    distributor = distributor_sales.objects.get(sales_person=sales_person)
                    # print(distributor.distributor.id,"distributor_id","====================",sales_person.id,"sales_person_id")
                    product_stock = DistributorStock.objects.get(distributor_id=distributor.distributor.id,
                                                                 product_id=sold_product.product_id)
                except DistributorStock.DoesNotExist:
                    product_stock = None

                if product_stock is None:
                    logger.error(f"You are trying to reduce product quantity which is not present in the distributor"
                                 f" stock list")
                else:
                    # Update existing DistributorStock entry
                    product_stock.quantity -= sold_product.quantity
                    product_stock.save()

            logger.info(f"Stock updated for Main Order {main_order.id}")
        except Exception as e:
            logger.error(f"Exception occurred in add_stock: {str(e)}")
            return str(e)

    try:
        salesPerson_orders.objects.create(sales_person=sales_person, order=main_order)
        reduce_stock(main_order)

        return True
    except Exception as e:
        logger.error("Exception: distributor_orders " + str(e))
        return False
