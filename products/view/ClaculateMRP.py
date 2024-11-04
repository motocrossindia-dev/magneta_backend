# from orders.models import GST
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission, IsDistributorPermission
from orders.models import GST
from products.serializers.MRPCalculationSerializer import GETMRPCalculationResultSerializer

logger = logging.getLogger("magneta_logger")


# def calculate_mrp(price, distributor_margin_rate, retailer_margin_rate, gst):
#     # gst = GST.objects.get(id=1).gst
#
#     factory_gst = round(price * (gst / 100), 2)
#
#     factory_sale = round(price + factory_gst, 2)
#
#     distributor_margin_price = round((factory_sale * (distributor_margin_rate / 100)), 2)
#
#     distributor_gst = round(distributor_margin_price * (gst / 100), 2)
#
#     distributor_sale = round(distributor_margin_price + distributor_gst + factory_sale, 2)
#
#     retailer_margin_price = round((distributor_sale * (retailer_margin_rate / 100)), 2)
#
#     retailer_gst = round(retailer_margin_price * (gst / 100), 2)
#
#     retailer_sale = round(retailer_margin_price + retailer_gst + distributor_sale, 2)
#
#     mrp = round(retailer_sale)
#
#     retailer_base_gst = round((mrp / (100 + gst)) * gst, 2)
#
#     retailer_base_price = round(mrp - retailer_base_gst, 2)
#
#     data = {'gst': gst, 'price': price, 'factory_gst': factory_gst,
#             'factory_sale': factory_sale, 'distributor_margin_rate': distributor_margin_rate,
#             'distributor_margin_price': distributor_margin_price, 'distributor_gst': distributor_gst,
#             'distributor_sale': distributor_sale, 'retailer_margin_rate': retailer_margin_rate,
#             'retailer_margin_price': retailer_margin_price, 'retailer_gst': retailer_gst,
#             'retailer_sale': retailer_sale, 'retailer_base_price': retailer_base_price,
#             'retailer_base_gst': retailer_base_gst, 'mrp': mrp
#             }
#     return data

def calculate_mrp(factory_sale, distributor_sale, mrp):
    gst = GST.objects.all().first().gst
    # print(gst,'---------gst')

    factory_gst = round(((factory_sale / (100 + gst)) * gst), 2)

    distributor_gst = round((((distributor_sale - factory_sale) / (100 + gst)) * gst), 2)

    retailer_gst = round((((mrp - distributor_sale) / (100 + gst)) * gst), 2)

    price = round((factory_sale - factory_gst), 2)

    distributor_margin_price = round((distributor_sale - factory_sale - distributor_gst),2)

    distributor_margin_rate = round(((distributor_margin_price / factory_sale) * 100), 2)

    retailer_margin_price = round((mrp - distributor_sale - retailer_gst), 2)

    retailer_margin_rate = round(((retailer_margin_price/ distributor_sale)*100), 2)

    retailer_base_gst = round(((mrp / (100 + gst)) * gst), 2)

    retailer_base_price = round((mrp - retailer_base_gst), 2)

    retailer_sale = mrp

    data = {'gst': gst, 'price': price, 'factory_gst': factory_gst,
            'factory_sale': factory_sale, 'distributor_margin_rate': distributor_margin_rate,
            'distributor_margin_price': distributor_margin_price, 'distributor_gst': distributor_gst,
            'distributor_sale': distributor_sale, 'retailer_margin_rate': retailer_margin_rate,
            'retailer_margin_price': retailer_margin_price, 'retailer_gst': retailer_gst,
            'retailer_sale': retailer_sale, 'retailer_base_price': retailer_base_price,
            'retailer_base_gst': retailer_base_gst, 'mrp': mrp
            }

    return data


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def get_mrp(request):
    if request.method == 'POST':
        try:
            factory_sale = float(request.data.get('factory_sale'))
            distributor_sale = float(request.data.get('distributor_sale'))
            mrp = float(request.data.get('mrp'))
            # price = request.data.get('price')
            # distributor_margin_rate = request.data.get('distributor_margin_rate')
            # retailer_margin_rate = request.data.get('retailer_margin')
            # data = calculate_mrp(price=price,
            #                      distributor_margin_rate=distributor_margin_rate,
            #                      retailer_margin_rate=retailer_margin_rate, gst=18)
            data = calculate_mrp(factory_sale, distributor_sale, mrp)
            serializer = GETMRPCalculationResultSerializer(data, context=request.data)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: get_mrp " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in get_mrp: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


if __name__ == '__main__':
    # Factory base price (fbp)
    p = 183.95

    # Distributor Margin rate (dmr)
    dmr = 14.00

    # Retailer margin rate (rmr)
    rmr = 25.00

    calculate_mrp(price=p, distributor_margin_rate=dmr, retailer_margin_rate=rmr, gst=18)
