import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsDistributorPermission
from orders.models import MainOrders
from orders.serializers.MainOrdersSerializer import PATCHmainOrdersSerializer
from orders.serializers.PaymentTrackSerializer import POSTPaymentTrackSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def verifying_payment(request, pk=None):
    if request.method == 'PATCH':
        try:
            main_order = get_object_or_404(MainOrders, pk=pk)
            main_order_data = request.data['main_order']
            main_order_serializer = PATCHmainOrdersSerializer(instance=main_order, data=main_order_data, partial=True)
            order_update_person_data = request.data['main_order']
            if main_order_serializer.is_valid():
                main_order_serializer.save()
                payment_track = {
                    'main_order': main_order.pk,
                    'status': main_order.status,
                    'updated_by': order_update_person_data.get('manager'),
                    'updator_contact': order_update_person_data.get('phone_number'),
                    'utrNo': order_update_person_data.get('utr_number', 0),
                    'cash': order_update_person_data.get('cashPayment', 0.00),
                    'cheque': order_update_person_data.get('cheque', 0),
                }
                payment_serializer = POSTPaymentTrackSerializer(data=payment_track)
                if payment_serializer.is_valid():
                    payment_serializer.save()
                else:
                    logger.error("Error in verifying_payment: ", str(payment_serializer.errors))
                    return Response(data={"error": payment_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.error("Error in verifying_payment: ", str(main_order_serializer.errors))
                return Response(data={"error": main_order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data={"msg": "Payment verified successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: verifying_payment " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in verifying_payment: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
