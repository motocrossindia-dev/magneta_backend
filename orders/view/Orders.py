import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission, IsDistributorPermission
from accounts.models import UserBase
from orders.models import Order, MainOrders, GST, PaymentTrack
from orders.serializers.MainOrdersSerializer import POSTMainOrdersSerializer, PATCHmainOrdersSerializer
from orders.serializers.OrderSerializer import GETordersSerializer, GETnameDateSerializer, PATCHordersSerializer, \
    POSTOrderSerializer
from django.shortcuts import get_object_or_404
from orders.serializers.PaymentTrackSerializer import POSTPaymentTrackSerializer, GETPaymentTrackSerializer
from orders.view.ManageStock import add_stock
from products.models import Product
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger("magneta_logger")


def apply_gst(main_order):
    distributor = get_object_or_404(UserBase, id=main_order.distributor.id)
    if distributor.gst is not None:  # Check if GST is not empty
        if distributor.gst[:2] == "29":
            # calculate CGST and SGST from GST on sub_total of main_order
            cgst = GST.objects.get(id=1).cgst
            sgst = GST.objects.get(id=1).sgst
            CGST = (main_order.sub_total * cgst) / 100
            main_order.CGST = round(CGST, 2)
            main_order.SGST = (main_order.sub_total * sgst) / 100
            main_order.SGST = round(main_order.SGST, 2)
            main_order.IGST = 0.00  # Format IGST as well

            main_order.CGST_rate = round(cgst, 2)
            main_order.SGST_rate = round(sgst, 2)
        else:
            # calculate IGST from GST on sub_total of main_order
            igst = GST.objects.get(id=1).igst
            IGST = (main_order.sub_total * igst) / 100
            main_order.IGST = round(IGST, 2)
            main_order.CGST = 0.00  # Format CGST as well
            main_order.SGST = 0.00  # Format SGST as well

            main_order.IGST_rate = round(igst, 2)

        main_order.gst_rate = round((main_order.CGST_rate + main_order.SGST_rate + main_order.IGST_rate), 2)
        main_order.gst = round((main_order.CGST + main_order.SGST + main_order.IGST), 2)
        main_order.save()
    else:
        print('GST information is not available for distributor', distributor)
        return 'GST information is not available for distributor', distributor


def calculate_sub_total(main_order):
    sub_total = 0
    orders_of_main_order = Order.objects.filter(main_order=main_order)
    for order in orders_of_main_order:
        sub_total += order.sum

    main_order.sub_total = round(sub_total, 2)
    main_order.save()
    return None


def calculate_grand_total(main_order):
    # Calculate Grand Total from sub_total, CGST, SGST, and IGST of main_order
    grand_total = float(main_order.sub_total) + float(main_order.CGST) + float(main_order.SGST) + float(main_order.IGST)

    main_order.grand_total = round(grand_total, 2)
    main_order.save()
    return None


def update_payment_track(main_order_data, pk):
    if (main_order_data.get('status') == "Amount Paid" or main_order_data.get('status') == "Verifying Payment" or
            main_order_data.get('status') == "Requested"):
        payment_track = {
            'main_order': pk,
            'status': main_order_data.get('status'),
            'updated_by': main_order_data.get('manager'),
            'updator_contact': main_order_data.get('phone_number'),
            'utrNo': main_order_data.get('utrNo'),
            'cash': main_order_data.get('cashPayment'),
            'cheque': main_order_data.get('chequePayment'),
        }
    else:
        payment_track = PaymentTrack.objects.filter(main_order=pk).last()
        payment_track = {
            'main_order': pk,
            'status': main_order_data.get('status'),
            'updated_by': main_order_data.get('manager'),
            'updator_contact': main_order_data.get('phone_number'),
            'utrNo': payment_track.utrNo,
            'cash': payment_track.cash,
            'cheque': payment_track.cheque,
        }
    payment_serializer = POSTPaymentTrackSerializer(data=payment_track)
    if payment_serializer.is_valid():
        payment_serializer.save()
    else:
        return Response(data={"error": payment_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def orders(request, pk=None):
    if request.method == 'GET' and pk is not None:
        try:
            order = Order.objects.filter(main_order=pk)
            serializer = GETordersSerializer(order, many=True)
            main_order = MainOrders.objects.filter(id=pk)
            serializer1 = GETnameDateSerializer(main_order, many=True)

            for data in serializer1.data:
                if data['mode_of_payment'] in ['stn', 'free sample']:
                    data['GST'] = 0.00
                    data['CGST'] = 0.00
                    data['SGST'] = 0.00
                    data['IGST'] = 0.00
                    data['CGST_rate'] = 0.00
                    data['IGST_rate'] = 0.00
                    data['SGST_rate'] = 0.00
                    data['gst_rate'] = 0.00
            if serializer1.data[0]['mode_of_payment'] == 'free sample' or serializer1.data[0]['mode_of_payment'] == 'stn':
                for data in serializer.data:
                    data['price_per_carton'] = 0.00
                    print(data)



            # get last payment track of a main order
            payment_track = PaymentTrack.objects.filter(main_order=pk).last()
            serializer2 = GETPaymentTrackSerializer(payment_track)
            print(serializer1.data)

            return Response(data={"data": serializer.data, "data1": serializer1.data, "data2": serializer2.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST' and pk is None:
        try:
            ordered_products = request.data.get('ordered_products', [])
            main_order_serializer = POSTMainOrdersSerializer(data=request.data['main_order'],
                                                             context={'request': ordered_products})
            main_order_data = request.data['main_order']
            if main_order_serializer.is_valid():
                main_order = main_order_serializer.save()
                for ordered_product_data in ordered_products:
                    product_id = ordered_product_data.get('id')
                    product = get_object_or_404(Product, pk=product_id)

                    ordered_product_data['product_name'] = product.pk
                    ordered_product_data['price_per_piece'] = product.factory_sale
                    ordered_product_data['carton_size'] = product.carton_size
                    ordered_product_data['price_per_carton'] = round(product.carton_size * product.price, 2)

                    ordered_product = POSTOrderSerializer(data=ordered_product_data)
                    if ordered_product.is_valid():
                        ordered_product = ordered_product.save(main_order=main_order)

                        ordered_product.save()
                    else:
                        logger.error("Error in orders: ", str(ordered_product.errors))
                        return Response(data={"error": ordered_product.errors},
                                        status=status.HTTP_400_BAD_REQUEST)

                calculate_sub_total(main_order=main_order)
                apply_gst(main_order=main_order)
                calculate_grand_total(main_order=main_order)
                print("main_order_data==============",main_order_data)
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

    elif request.method == 'PATCH' and pk is not None:
        try:
            gst = GST.objects.get(id=1)
            main_order_data = request.data['main_order']
            if main_order_data['status'] == 'Accepted':
                main_order = get_object_or_404(MainOrders, pk=pk)
                main_order_serializer = PATCHmainOrdersSerializer(instance=main_order, data=main_order_data,
                                                                  partial=True)
                if main_order_serializer.is_valid():
                    main_order = main_order_serializer.save()
                    ordered_products = request.data.get('ordered_products', [])
                    for ordered_product_data in ordered_products:
                        order_instance = get_object_or_404(Order, pk=ordered_product_data.get('id'))
                        product = get_object_or_404(Product, pk=order_instance.product_name.id)

                        # ordered_product_data['discount_amount'] = round((order_instance.price_per_carton *
                        #                                                  ordered_product_data['accepted_quantity'] *
                        #                                                  ordered_product_data['discount'] / 100), 2)
                        ordered_product_data['factory_base_price'] = product.price
                        ordered_product_data['factory_gst_price'] = product.factory_gst
                        ordered_product_data['factory_sale'] = product.factory_sale
                        ordered_product_data['mrp'] = product.mrp
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

                        serializer = PATCHordersSerializer(instance=order_instance,
                                                           data=ordered_product_data, partial=True)

                        if serializer.is_valid():
                            serializer.save()

                        else:
                            logger.error("Error in orders: ", str(serializer.errors))
                            return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    main_order = get_object_or_404(MainOrders, pk=pk)
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

                    data = {"status": main_order_data['status'],
                            "utrNo": main_order_data['utrNo'],
                            "cashPayment": main_order_data['cashPayment'],
                            "chequePayment": main_order_data['chequePayment'],
                            "creditOtp": main_order_data['creditOtp'],
                            "manager": main_order_data['manager'],
                            "phone_number": main_order_data['phone_number']}
                    update_payment_track(main_order_data=data, pk=pk)
                    return Response(data={"msg": "orders status changed to Accepted"}, status=status.HTTP_200_OK)
                elif main_order_serializer.errors:
                    logger.error("Error in orders: ", str(main_order_serializer.errors))
                    return Response(data={"error": main_order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            elif main_order_data['status'] == 'Verifying Payment':
                main_order = get_object_or_404(MainOrders, pk=pk)
                main_order.mode_of_payment = main_order_data['mode_of_payment']
                main_order.save()

                update_payment_track(main_order_data=main_order_data, pk=pk)
                return Response(data={"msg": "orders status changed to Cancelled"}, status=status.HTTP_200_OK)

            elif main_order_data['status'] == 'Amount Paid':
                main_order = get_object_or_404(MainOrders, pk=pk)
                main_order.payment_status = 'Paid'
                main_order.status = 'Amount Paid'
                main_order.save()

                data = {"status": main_order_data['status'],
                        "utrNo": main_order_data['utrNo'],
                        "cashPayment": main_order_data['cashPayment'],
                        "chequePayment": main_order_data['chequePayment'],
                        "creditOtp": main_order_data['creditOtp'],
                        "manager": main_order_data['manager'],
                        "phone_number": main_order_data['phone_number']}

                update_payment_track(main_order_data=data, pk=pk)
                return Response(data={"msg": "orders status changed to Amount Paid"}, status=status.HTTP_200_OK)

            elif main_order_data['status'] == 'In Process':
                main_order = get_object_or_404(MainOrders, pk=pk)
                main_order.status = 'In Process'
                main_order.save()

                update_payment_track(main_order_data=main_order_data, pk=pk)
                return Response(data={"msg": "orders status changed to In Process"}, status=status.HTTP_200_OK)

            elif main_order_data['status'] == 'Dispatched':
                main_order = get_object_or_404(MainOrders, pk=pk)
                main_order.status = 'Dispatched'
                main_order.save()

                update_payment_track(main_order_data=main_order_data, pk=pk)
                return Response(data={"msg": "orders status changed to Dispatched"}, status=status.HTTP_200_OK)

            elif main_order_data['status'] == 'Delivered':
                main_order = get_object_or_404(MainOrders, pk=pk)
                main_order.status = 'Delivered'
                main_order.save()

                print("near add_stock")
                add_stock(main_order=main_order)

                update_payment_track(main_order_data=main_order_data, pk=pk)
                return Response(data={"msg": "orders status changed to Delivered"}, status=status.HTTP_200_OK)

            elif main_order_data['status'] == 'Cancelled':
                main_order = get_object_or_404(MainOrders, pk=pk)
                if (main_order_data.get('status') == 'Cancelled' and
                        (main_order.status == 'Requested' or main_order.status == 'Accepted')):
                    main_order.status = 'Cancelled'
                    main_order.save()
                    update_payment_track(main_order_data=main_order_data, pk=pk)
                    return Response(data={"msg": "Orders cancelled"}, status=status.HTTP_200_OK)
                else:
                    return Response(data={"msg": "Order is in process you can't cancel."},
                                    status=status.HTTP_400_BAD_REQUEST)

            else:
                logger.error("Error in orders: Invalid request")
                return Response(data={"error": "Required to change status."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error("Exception: orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated, IsDistributorPermission])
@authentication_classes([JWTAuthentication])
def distributor_orders(request, pk=None):
    if request.method == 'GET' and pk is not None:
        try:
            order = Order.objects.filter(main_order=pk)
            serializer = GETordersSerializer(order, many=True)
            main_order = MainOrders.objects.filter(id=pk)
            serializer1 = GETnameDateSerializer(main_order, many=True)
            print(serializer1.data, "serializer1.data")

            print("user orders,'==============",serializer.data)

            return Response(data={"data": serializer.data, "data1": serializer1.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: distributor_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST' and pk is None:
        try:
            ordered_products = request.data.get('ordered_products', [])
            main_order_serializer = POSTMainOrdersSerializer(data=request.data['main_order'],
                                                             context={'request': ordered_products})
            if main_order_serializer.is_valid():
                main_order = main_order_serializer.save()
                for ordered_product_data in ordered_products:
                    product_id = ordered_product_data.get('id')
                    product = get_object_or_404(Product, pk=product_id)

                    ordered_product_data['product_name'] = product.pk
                    ordered_product_data['carton_size'] = product.carton_size
                    ordered_product_data['price_per_carton'] = round((product.carton_size * product.price), 2)
                    ordered_product_data['accepted_quantity'] = ordered_product_data['requested_quantity']

                    ordered_product = POSTOrderSerializer(data=ordered_product_data)
                    if ordered_product.is_valid():
                        ordered_product = ordered_product.save(main_order=main_order)

                        ordered_product.save()
                    else:
                        logger.error("Error in orders: ", str(ordered_product.errors))
                        return Response(data={"error": ordered_product.errors},
                                        status=status.HTTP_400_BAD_REQUEST)

                calculate_sub_total(main_order=main_order)
                apply_gst(main_order=main_order)
                calculate_grand_total(main_order=main_order)

                main_order_data = request.data['main_order']
                main_order_data['manager'] = str(request.user)

                data = {"status": main_order_data['status'],
                        "utrNo": "0",
                        "cashPayment": 0.00,
                        "chequePayment": 0,
                        "creditOtp": 0.00,
                        "manager": main_order_data['manager'],
                        "phone_number": main_order_data['phone_number']}

                update_payment_track(main_order_data=data, pk=main_order.id)
                # update_payment_track(main_order_data=request.data['main_order'], pk=main_order.id)
                return Response(data={"msg": "Orders created"}, status=status.HTTP_200_OK)
            else:
                logger.error("Error in orders: ", str(main_order_serializer.errors))
                return Response(data={"error": main_order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: distributor_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH' and pk is not None:
        try:
            main_order = get_object_or_404(MainOrders, pk=pk)
            main_order_data = request.data['main_order']
            if (main_order_data.get('status') == 'Cancelled' and
                    (main_order.status == 'Requested' or main_order.status == 'Accepted')):
                main_order.status = 'Cancelled'
                main_order.save()
                update_payment_track(main_order_data=main_order_data, pk=pk)
                return Response(data={"msg": "Orders cancelled"}, status=status.HTTP_200_OK)

            elif main_order_data.get('status') == 'Delivered':
                main_order.status = 'Delivered'
                main_order.save()
                add_stock(main_order=main_order)
                update_payment_track(main_order_data=main_order_data, pk=pk)
                return Response(data={"msg": "Orders Delivered"}, status=status.HTTP_200_OK)

            elif main_order_data.get('status') in ['Amount Paid', 'In process', 'Dispatched', 'Delivered']:
                return Response(data={"msg": f"Order is in {main_order_data.get('status')} you can't cancel."},
                                status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response(data={"msg": "Order is already in " + main_order_data.get('status')},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: distributor_orders " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
