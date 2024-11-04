import logging
from datetime import timedelta

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerOrDistributorPermission, IsDistributorPermission
from accounts.models import UserBase
from distributors.models import RetailerOrders, RetailerMainOrders
from distributors.serializers.RetailerMainOrderSerializer import POSTretailerMainOrdersSerializer, \
    GETretailerMainOrderSerializer
from django.shortcuts import get_object_or_404

from distributors.serializers.RetailerOrderSerializer import POSTretailerOrderSerializer, GETretailerOrderSerializer
from orders.models import GST
from orders.view.ManageStock import reduce_stock
from products.models import Product
from django.apps import apps
from django.utils import timezone

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsManagerOrDistributorPermission])
@authentication_classes([JWTAuthentication])
def retailer_orders(request, pk=None):
    user = request.user
    gst = GST.objects.get(id=1)
    
    if request.method == 'GET' and (user.is_distributor or user.is_manager) and pk is not None:
        try:
            
            main_order = get_object_or_404(RetailerMainOrders, pk=pk)
            order_details = RetailerOrders.objects.filter(retailer_main_order=pk)
            serializer = GETretailerOrderSerializer(order_details, many=True)
            return Response(data={"data": serializer.data, "order_number": main_order.order_number},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: distributor_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST' and (user.is_distributor or user.is_manager) and pk is None:
        ordered_products = request.data.get('ordered_products', [])
        print(ordered_products, "ordered_products")
        main_order = request.data.get('main_order', {})
        # main_order['distributor'] = user.pk

        main_order_serializer = POSTretailerMainOrdersSerializer(data=main_order, context={'request': ordered_products})
        if main_order_serializer.is_valid():
            mode_of_payment = main_order.get('mode_of_payment')
            if mode_of_payment == 'credit':
                payment_status = "Unpaid"
                
            else:
                payment_status = "Paid"
            main_order = main_order_serializer.save(distributor=user, payment_status=payment_status)
            if user.is_manager:
                main_order.order_by_factory = True
                main_order.save()
                print(main_order)
            for ordered_product_data in ordered_products:
                product_id = ordered_product_data.get('product_id')
                print(product_id, "product_id")
                product = get_object_or_404(Product, pk=product_id)
                print(product.factory_sale, "product factory_sale")
                # Fetch price from product and assign it to price_per_piece

                ordered_product_data['retailer_main_order'] = main_order.pk
                ordered_product_data['product_id'] = product.pk
                ordered_product_data['product_name'] = product.product_name
                ordered_product_data['distributor_margin_rate'] = product.distributor_margin_rate
                ordered_product_data['distributor_margin_price'] = product.distributor_margin_price
                ordered_product_data['distributor_gst'] = product.distributor_gst
                ordered_product_data['distributor_sale'] = product.distributor_sale
                ordered_product_data['carton_size'] = product.carton_size
                ordered_product_data['mrp'] = product.mrp

                # price per carton =======================================================
                ordered_product_data['price_per_carton'] = round(
                    (product.distributor_sale * product.carton_size) / (1 + (product.gst / 100)), 2)
                # ========================================================================

                # total gst calculation ===================================================
                gst_per_carton = round(
                    (product.distributor_sale * product.carton_size) - (
                            product.distributor_sale * product.carton_size) / (1 + (product.gst / 100)), 2)
                ordered_product_data['gst'] = round(gst_per_carton * ordered_product_data['quantity'], 2)
                # =========================================================================================

                print(ordered_product_data['price_per_carton'], "price_per_carton")

                # ordered_product_data['sum'] = round((ordered_product_data['quantity'] * product.carton_size *
                #                                      (product.factory_sale + product.distributor_margin_price)), 2)

                # sum calculations ===============================================================================
                ordered_product_data['sum'] = round(
                    (ordered_product_data['quantity'] * ordered_product_data['price_per_carton']), 2)
                # ================================================================================================

                # amount calculations
                ordered_product_data['amount'] = round(ordered_product_data['sum'] + ordered_product_data['gst'], 2)

                # gst split calculations ==========================================================================
                retailer = UserBase.objects.get(pk=main_order.retailer_id)
                if retailer.gst[:2] == "29":
                    ordered_product_data['CGST'] = round(ordered_product_data['gst'] / 2, 2)
                    ordered_product_data['SGST'] = round(ordered_product_data['gst'] / 2, 2)

                else:
                    ordered_product_data['IGST'] = round(ordered_product_data['gst'], 2)

                # ================================================================================================

                ordered_product_data['amount'] = round((ordered_product_data['sum'] + ordered_product_data['gst']), 2)

                ordered_product = POSTretailerOrderSerializer(data=ordered_product_data)
                if ordered_product.is_valid():
                    ordered_product = ordered_product.save()
                    ordered_product.save()
                else:
                    logger.error("Error in orders: ", str(ordered_product.errors))
                    return Response(data={"error": ordered_product.errors},
                                    status=status.HTTP_400_BAD_REQUEST)

            # sgst_total = sum(ordered_product.SGST for ordered_product in main_order.retailer_orders.all())
            ordered_products = RetailerOrders.objects.filter(retailer_main_order=main_order).all()
            sub_total = sum(ordered_product.sum for ordered_product in ordered_products)

            if retailer.gst[:2] == "29":
                main_order.CGST = round((sub_total * gst.cgst) / 100, 2)
                main_order.SGST = round((sub_total * gst.sgst) / 100, 2)
                main_order.IGST = 0
                main_order.gst = (main_order.CGST + main_order.SGST + main_order.IGST)

                main_order.CGST_rate = round(gst.cgst, 2)
                main_order.SGST_rate = round(gst.sgst, 2)
                main_order.IGST_rate = 0
                main_order.gst_rate = round((main_order.CGST_rate + main_order.SGST_rate + main_order.IGST_rate), 2)
            else:
                main_order.CGST = 0
                main_order.SGST = 0
                main_order.IGST = round((sub_total * gst.igst) / 100, 2)
                main_order.gst = (main_order.CGST + main_order.SGST + main_order.IGST)

                main_order.CGST_rate = 0
                main_order.SGST_rate = 0
                main_order.IGST_rate = round(gst.igst, 2)
                main_order.gst_rate = round((main_order.CGST_rate + main_order.SGST_rate + main_order.IGST_rate), 2)

            main_order.sub_total = round(sub_total, 2)
            main_order.grand_total = round((sub_total + main_order.gst), 2)


            # ################################################################################

            # Generate order number
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            last_order = RetailerMainOrders.objects.filter(order_date__range=(today_start, today_end)).order_by(
                '-order_number').first()

            if last_order:
                last_order_number = int(last_order.order_number[7:]) + 1
            else:
                last_order_number = 1

            if last_order_number > 9999:
                raise ValueError("Maximum orders exceeded for the day.")

            app_name = apps.get_app_config('distributors').name[0].upper()
            order_number = (f"{app_name}{str(today_start.year)[-2:]}{today_start.month:02d}{today_start.day:02d}"
                            f"{last_order_number:04d}")
            main_order.order_number = order_number

            #####################################################################################################

            # main_order.order_number = order_number
            main_order.save()

            # ##################################### reduce stock ################################################
            reduce_stock(main_order=main_order)
            #####################################################################################################

            return Response(data={"msg": "order created successfully.", "main_order_id": main_order.id,
                                  "order_number": main_order.order_number}, status=status.HTTP_200_OK)
        else:
            logger.error("Error in retailer_orders: " + str(main_order_serializer.errors))
            return Response(data={"error": main_order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        # return Response(data={"msg": "order created !!!!"}, status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        try:

            mode_of_payment = request.data.get('mode_of_payment', "cash")
            payment_status = request.data.get('payment_status', 'Unpaid')
            order = RetailerMainOrders.objects.get(id=pk)

            order.payment_status = payment_status
            order.mode_of_payment = mode_of_payment

            order.save()
            return Response(data={"success": "Successfully updated order", "order_id": pk},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: distributor_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsDistributorPermission])
@authentication_classes([JWTAuthentication])
def distributor_today_collection(request):
    user = request.user
    if request.method == 'GET':
        try:
            distributor = UserBase.objects.get(id=user.id)

            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            main_orders = RetailerMainOrders.objects.filter(distributor=distributor,
                                                            order_date__range=(today_start, today_end))

            total_collection = 0
            for main_order in main_orders:
                total_collection += main_order.grand_total

            return Response(data={"total_collection": total_collection, "bill_generated": main_orders.count()},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in distributor_today_collection: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
