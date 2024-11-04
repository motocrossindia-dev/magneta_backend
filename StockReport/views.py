# # Create your views here.
import shutil

from django.conf import settings
from django.db.models import ProtectedError
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import StockRecord
from .serializers import StockRecordUpdateSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from django.core.files import File
import os

from StockReport.serializers import ProductsSerializer, ProductStockRecordCreateSerializer
from products.models import Product
from .pdf_generator import generate_comprehensive_stock_pdf


class ProductsOpeningStockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows OpeningStock to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductsSerializer



from rest_framework import generics


class ProductStockRecordViewSet(generics.CreateAPIView):
    serializer_class = ProductStockRecordCreateSerializer

    def post(self, request, format=None):
        print(request.data, '-----request-------data')

        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product stock record successfully created"}, status=status.HTTP_201_CREATED)
        else:
            error_message = self.get_error_message(serializer.errors)
            return Response({"message": f"Failed to create product stock record. {error_message}"}, status=status.HTTP_400_BAD_REQUEST)

    def get_error_message(self, errors):
        error_messages = []
        for field, messages in errors.items():
            if field == 'non_field_errors':
                error_messages.extend(messages)
            elif isinstance(messages, list):
                error_messages.append(f"{field}: {', '.join(messages)}")
            elif isinstance(messages, dict):
                nested_messages = self.get_error_message(messages)
                error_messages.append(f"{field}: {nested_messages}")
            else:
                error_messages.append(f"{field}: {messages}")
        return '. '.join(error_messages) if error_messages else "An unknown error occurred."
    # def get_error_message(self, errors):
    #     error_messages = []
    #     for field, messages in errors.items():
    #         if isinstance(messages, list):
    #             error_messages.append(f"{field}: {', '.join(messages)}")
    #         elif isinstance(messages, dict):
    #             nested_messages = self.get_error_message(messages)
    #             error_messages.append(f"{field}: {nested_messages}")
    #         else:
    #             error_messages.append(f"{field}: {messages}")
    #     return '. '.join(error_messages) if error_messages else "An unknown error occurred."
# class ProductStockRecordViewSet(generics.CreateAPIView):
#     def post(self, request, format=None):
#         print(request.data,'-----request-------data')
#
#         serializer = ProductStockRecordCreateSerializer(data=request.data,context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message":"successfully recorded"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
from rest_framework import viewsets
from .models import StockRecord
from .serializers import StockRecordSerializer

import django_filters

from django.conf import settings
from django.utils import timezone
#

class StockFilter(django_filters.FilterSet):
    # OpeningStock Date Filters
    date = django_filters.DateFilter(field_name='date')

    class Meta:
        model = StockRecord
        fields = ['date']


class StockRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows StockRecord to be viewed or edited.
    """
    queryset = StockRecord.objects.all().order_by('-id')
    serializer_class = StockRecordSerializer
    filterset_class = StockFilter

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_editable:
            return Response({"detail": "This record is not editable."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_editable:
            return Response({"detail": "This record is not editable."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    # @action(detail=True, methods=['get'])
    # def generate_pdf(self, request, pk=None):
    #     stock_record = self.get_object()
    #     pdf_filename = generate_comprehensive_stock_pdf(stock_record)
    #
    #     # Save the file path to the StockRecord instance
    #     with open(pdf_filename, 'rb') as file:
    #         stock_record.generated_file.save(os.path.basename(pdf_filename), File(file))
    #
    #     # Construct the full URL to the file
    #     file_url = request.build_absolute_uri(stock_record.generated_file.url)
    #
    #     # Delete the temporary file
    #     os.remove(pdf_filename)
    #
    #     return Response({
    #         'message': 'PDF generated successfully',
    #         'file_url': file_url
    #     }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Report deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError as e:
            protected_objects = list(e.protected_objects)
            error_message = f"Cannot delete this product type because it is referenced by {len(protected_objects)} product(s)."
            return Response({"message": error_message, "protected_objects": [str(obj) for obj in protected_objects]},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"An error occurred while deleting the product type: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# <editor-fold desc="stock records update how to do">

# views.py


class StockRecordUpdateView(generics.UpdateAPIView):
    queryset = StockRecord.objects.all()
    serializer_class = StockRecordUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_editable:
            return Response({"message": "This stock record is not editable."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return Response({"message": f"Failed to update stock record. {self.get_error_message(serializer.errors)}"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_update(serializer)
            return Response({"message": "Stock record updated successfully", "data": serializer.data})
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        serializer.save()
        stock_record = serializer.instance
        pdf_path = self.generate_and_save_pdf(stock_record)
        self.save_pdf_to_model(stock_record, pdf_path)

    def generate_and_save_pdf(self, stock_record):
        original_pdf_path = generate_comprehensive_stock_pdf(stock_record)
        reports_dir = os.path.join(settings.BASE_DIR, 'stock_reports')
        os.makedirs(reports_dir, exist_ok=True)
        new_pdf_filename = f"stock_report_{stock_record.id}_{timezone.now().strftime('%d%m%Y_%H%M%S')}.pdf"
        new_pdf_path = os.path.join(reports_dir, new_pdf_filename)
        shutil.move(original_pdf_path, new_pdf_path)
        return new_pdf_path

    def save_pdf_to_model(self, stock_record, pdf_path):
        with open(pdf_path, 'rb') as file:
            stock_record.generated_file.save(os.path.basename(pdf_path), File(file))

    @staticmethod
    def get_error_message(errors):
        return '. '.join(f"{field}: {', '.join(messages) if isinstance(messages, list) else messages}"
                         for field, messages in errors.items())
    # def update(self, request, *args, **kwargs):
    #     print(request.data,'----------------------data')
    #     # Get the access token from the Authorization header
    #
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     if instance and not instance.is_editable:
    #         raise Response({"message": "This stock record is not editable.","status":status.HTTP_403_FORBIDDEN})
    #
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #
    #     if not serializer.is_valid():
    #         error_message = self.get_error_message(serializer.errors)
    #         return Response({
    #             "message": f"Failed to update stock record. {error_message}"
    #         }, status=status.HTTP_400_BAD_REQUEST)
    #
    #     try:
    #         self.perform_update(serializer)
    #
    #         if getattr(instance, '_prefetched_objects_cache', None):
    #             instance._prefetched_objects_cache = {}
    #
    #         return Response({
    #             "message": "Stock record updated successfully",
    #             "data": serializer.data
    #         }, status=status.HTTP_200_OK)
    #
    #     except Exception as e:
    #         return Response({
    #             "message": f"An error occurred while updating the stock record: {str(e)}"
    #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    # def perform_update(self, serializer):
    #     try:
    #         serializer.save()
    #         stock_record = serializer.instance
    #
    #         # Generate the PDF using the existing function
    #         original_pdf_path = generate_comprehensive_stock_pdf(stock_record)
    #
    #         # Create stock_reports directory if it doesn't exist
    #         reports_dir = os.path.join(settings.BASE_DIR, 'stock_reports')
    #         os.makedirs(reports_dir, exist_ok=True)
    #
    #         # Generate a new file name
    #         timestamp = timezone.now().strftime('%d%m%Y_%H%M%S')
    #         new_pdf_filename = f"stock_report_{stock_record.id}_{timestamp}.pdf"
    #         new_pdf_path = os.path.join(reports_dir, new_pdf_filename)
    #
    #         # Move the generated PDF to the stock_reports directory
    #         shutil.move(original_pdf_path, new_pdf_path)
    #
    #         # Save the generated file to the model
    #         with open(new_pdf_path, 'rb') as file:
    #             stock_record.generated_file.save(new_pdf_filename, File(file))
    #
    #     except Exception as e:
    #         raise Exception(f"Error in perform_update: {str(e)}")
    #
    # def get_error_message(self, errors):
    #     error_messages = []
    #     for field, messages in errors.items():
    #         if isinstance(messages, list):
    #             error_messages.append(f"{field}: {', '.join(messages)}")
    #         else:
    #             error_messages.append(f"{field}: {messages}")
    #     return '. '.join(error_messages) if error_messages else "An unknown error occurred."
    #

# class StockRecordUpdateView(generics.UpdateAPIView):
#     queryset = StockRecord.objects.all()
#     serializer_class = StockRecordUpdateSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     lookup_field = 'id'
#
#     def update(self, request, *args, **kwargs):
#         print(request.data,'----------------------data')
#         # Get the access token from the Authorization header
#         auth_header = request.META.get('HTTP_AUTHORIZATION')
#         if auth_header and auth_header.startswith('Bearer '):
#             access_token = auth_header.split(' ')[1]
#             print('Access Token:', access_token)
#         else:
#             print('No valid access token found in the request')
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#
#         if not serializer.is_valid():
#             error_message = self.get_error_message(serializer.errors)
#             return Response({
#                 "message": f"Failed to update stock record. {error_message}"
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             self.perform_update(serializer)
#
#             if getattr(instance, '_prefetched_objects_cache', None):
#                 instance._prefetched_objects_cache = {}
#
#             return Response({
#                 "message": "Stock record updated successfully",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return Response({
#                 "message": f"An error occurred while updating the stock record: {str(e)}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#     def perform_update(self, serializer):
#         try:
#             serializer.save()
#             stock_record = serializer.instance
#             pdf_filename = generate_comprehensive_stock_pdf(stock_record)
#             with open(pdf_filename, 'rb') as file:
#                 stock_record.generated_file.save(os.path.basename(pdf_filename), File(file))
#         except Exception as e:
#             raise Exception(f"Error in perform_update: {str(e)}")
#
#     def get_error_message(self, errors):
#         error_messages = []
#         for field, messages in errors.items():
#             if isinstance(messages, list):
#                 error_messages.append(f"{field}: {', '.join(messages)}")
#             else:
#                 error_messages.append(f"{field}: {messages}")
#         return '. '.join(error_messages) if error_messages else "An unknown error occurred."
# class StockRecordUpdateView(generics.UpdateAPIView):
#     queryset = StockRecord.objects.all()
#     serializer_class = StockRecordUpdateSerializer
#     lookup_field = 'id'  # Change this line
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#
#         if getattr(instance, '_prefetched_objects_cache', None):
#             instance._prefetched_objects_cache = {}
#
#         return Response(serializer.data)
#
#     def perform_update(self, serializer):
#         serializer.save()
#         # After updating, you might want to regenerate the PDF
#         stock_record = serializer.instance
#         pdf_filename = generate_comprehensive_stock_pdf(stock_record)
#         with open(pdf_filename, 'rb') as file:
#             stock_record.generated_file.save(os.path.basename(pdf_filename), File(file))

# class StockRecordUpdateView(generics.UpdateAPIView):
#     queryset = StockRecord.objects.all()
#     serializer_class = StockRecordSerializer
#     lookup_field = 'id'
#
#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#
#         # Check if the record is editable
#         if not instance.is_editable:
#             return Response({"detail": "This record is not editable."}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Get the data for StockRecord
#         stock_record_data = request.data.copy()
#         product_stock_records_data = stock_record_data.pop('stock_record', [])
#
#         # Update StockRecord
#         serializer = self.get_serializer(instance, data=stock_record_data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#
#         # Update associated ProductStockRecords
#         for product_stock_record_data in product_stock_records_data:
#             product_stock_record_id = product_stock_record_data.get('id')
#             if product_stock_record_id:
#                 product_stock_record = ProductStockRecord.objects.get(id=product_stock_record_id)
#                 product_serializer = StockRecordUpdateSerializer(product_stock_record, data=product_stock_record_data,
#                                                                   partial=True)
#                 product_serializer.is_valid(raise_exception=True)
#                 product_serializer.save()
#
#         return Response(serializer.data)
# </editor-fold>

