from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.models import Product

import logging

from sales.models import ProductDiscount
from sales.serializers.ProductSerializer import GETProductSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET'])
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

            # Get the max discounts from the ProductDiscount model
            product_discount = ProductDiscount.objects.first()  # Assuming you have at least one entry
            if product_discount:
                max_product_discount = product_discount.max_product_discount
                max_invoice_discount = product_discount.max_invoice_discount
            else:
                max_product_discount = 0.00  # Default value if no discount is found
                max_invoice_discount = 0.00  # Default value if no discount is found

            return Response(data={"data": serializer.data, "max_product_discount": max_product_discount,
                "max_invoice_discount": max_invoice_discount}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":f"something went wrong{e}"}, status=status.HTTP_400_BAD_REQUEST)

