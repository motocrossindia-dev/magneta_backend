from rest_framework import viewsets

from sales.models import ProductDiscount
from sales.serializers.productdiscountSerializers import ProductDiscountSerializer


class ProductDiscountViewSet(viewsets.ModelViewSet):
    queryset = ProductDiscount.objects.all()  # Queryset for all product discounts
    serializer_class = ProductDiscountSerializer

    def create(self, request, *args, **kwargs):
        # Check if there's already an existing record
        if ProductDiscount.objects.exists():
            return Response({
                'message': 'Failed to create product discount. Only one record is allowed.',
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Product discount created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'message': 'Failed to create product discount.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Product discount updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Failed to update product discount.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

class ProductDiscountView(generics.GenericAPIView):
    serializer_class = ProductDiscountSerializer

    def get_queryset(self):
        # Return all ProductDiscount instances (but we expect to only deal with one)
        return ProductDiscount.objects.all()

    def get(self, request, *args, **kwargs):
        # Retrieve the first (and only) record
        instance = self.get_queryset().first()
        if instance is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)  # Return the single record data


