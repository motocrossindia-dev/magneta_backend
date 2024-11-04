import logging
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from accounts.models import UserBase
from orders.models import GST, MainOrders
from orders.serializers.MainOrdersSerializer import POSTMainOrdersSerializer
from orders.serializers.OrderSerializer import POSTOrderSerializer, POSTdirectFactoryOrderSerializer
from orders.serializers.PaymentTrackSerializer import POSTPaymentTrackSerializer
from orders.view.ManageStock import add_stock
from orders.view.Orders import calculate_sub_total, apply_gst, calculate_grand_total
from products.models import Product

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def factory_direct_sale(request):
    if request.method == 'POST':
        try:
            gst = GST.objects.get(id=1)
            ordered_products = request.data.get('ordered_products', [])
            main_order_serializer = POSTMainOrdersSerializer(data=request.data['main_order'],
                                                             context={'request': ordered_products})
            main_order_data = request.data['main_order']
            if main_order_serializer.is_valid():
                main_order = main_order_serializer.save()
                for ordered_product_data in ordered_products:
                    product_id = ordered_product_data.get('product_id')
                    product = get_object_or_404(Product, pk=product_id)

                    ordered_product_data['product_name'] = product.pk
                    ordered_product_data['factory_base_price'] = product.price
                    ordered_product_data['factory_gst_price'] = product.factory_gst
                    ordered_product_data['factory_sale'] = product.factory_sale
                    ordered_product_data['mrp'] = product.mrp
                    if main_order_data.get('mode_of_payment') == 'stn' or main_order_data.get('mode_of_payment') == 'free sample':
                        ordered_product_data['sum'] = 0.00
                        # distributor = UserBase.objects.get(pk=main_order.distributor_id)

                        ordered_product_data['CGST'] = 0.00
                        ordered_product_data['SGST'] = 0.00
                        ordered_product_data['IGST'] = 0.00
                        ordered_product_data['gst'] = 0.00
                        ordered_product_data['amount'] = 0.00
                        ordered_product_data['price_per_piece'] = 0.00
                        ordered_product_data['carton_size'] = product.carton_size
                        ordered_product_data['price_per_carton'] = 0.00

                    else:
                        ordered_product_data['sum'] = round((product.price * product.carton_size *
                                                         ordered_product_data['accepted_quantity']), 2)

                        distributor = UserBase.objects.get(pk=main_order.distributor_id)

                        if distributor.gst[:2] == "29":
                            ordered_product_data['CGST'] = round((ordered_product_data['sum'] * gst.cgst) / 100, 2)
                            ordered_product_data['SGST'] = round((ordered_product_data['sum'] * gst.sgst) / 100, 2)
                            ordered_product_data['IGST'] = 0
                            ordered_product_data['gst'] = (
                                    ordered_product_data['CGST'] + ordered_product_data['SGST'] +
                                    ordered_product_data['IGST'])
                        else:
                            ordered_product_data['CGST'] = 0
                            ordered_product_data['SGST'] = 0
                            ordered_product_data['IGST'] = round((ordered_product_data['sum'] * gst.igst) / 100, 2)
                            ordered_product_data['gst'] = (
                                    ordered_product_data['CGST'] + ordered_product_data['SGST'] +
                                    ordered_product_data['IGST'])

                            ordered_product_data['amount'] = round(
                                (ordered_product_data['sum'] + ordered_product_data['gst']), 2)

                        ordered_product_data['price_per_piece'] = product.factory_sale
                        ordered_product_data['carton_size'] = product.carton_size
                        ordered_product_data['price_per_carton'] = round(product.carton_size * product.price, 5)

                    ordered_product = POSTdirectFactoryOrderSerializer(data=ordered_product_data)
                    if ordered_product.is_valid():
                        ordered_product = ordered_product.save(main_order=main_order)

                        ordered_product.save()
                    else:
                        logger.error("Error in orders: ", str(ordered_product.errors))
                        return Response(data={"error": ordered_product.errors},
                                        status=status.HTTP_400_BAD_REQUEST)

                if main_order_data.get('mode_of_payment') == 'credit':
                    main_order.payment_status = 'Unpaid'
                    main_order.save()
                else:
                    main_order.payment_status = 'Paid'
                    main_order.save()

                calculate_sub_total(main_order=main_order)
                apply_gst(main_order=main_order)
                calculate_grand_total(main_order=main_order)

                # Generate order number
                today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = today_start + timedelta(days=1)

                last_order = MainOrders.objects.filter(order_date__range=(today_start, today_end)).order_by(
                    '-order_number').first()

                if last_order:
                    last_order_number = int(last_order.order_number[7:]) + 1
                else:
                    last_order_number = 1

                if last_order_number > 9999:
                    raise ValueError("Maximum orders exceeded for the day.")

                app_name = "F"
                order_number = (
                    f"{app_name}{str(today_start.year)[-2:]}{today_start.month:02d}{today_start.day:02d}"
                    f"{last_order_number:04d}")
                main_order.order_number = order_number
                main_order.save()

                add_stock(main_order=main_order)

                payment_track = {
                    'main_order': main_order.pk,
                    'status': main_order_data.get('status'),
                    'updated_by': main_order_data.get('manager'),
                    'updator_contact': main_order_data.get('phone_number'),
                    'utrNo': main_order_data.get('utrNo', 0),
                    'cash': main_order_data.get('cashPayment', 0.00),
                    'cheque': main_order_data.get('chequePayment', 0),
                }
                payment_serializer = POSTPaymentTrackSerializer(data=payment_track)
                if payment_serializer.is_valid():
                    payment_serializer.save()
                else:
                    return Response(data={"error": payment_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
                return Response(data={"msg": "Orders created...."}, status=status.HTTP_200_OK)
            else:
                logger.error("Error in orders: ", str(main_order_serializer.errors))
                return Response(data={"error": main_order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
