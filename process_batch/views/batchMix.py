
import logging
from datetime import timedelta, datetime

from django.utils import timezone
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# from inventory.view.GRN import update_process_store
from process_batch.models.BatchMix import BatchMix
from process_batch.serializers.BatchMixSerializer import BatchMixSerializer, GetBatchMixSerializer, \
    BatchMixCreateSerializer, BatchMixUpdateSerializer, GetBatchMixDetailSerializer, BatchMixUpdateExpiredSerializer, \
    BatchMixIcreamGetTemplateDetailsSerializer, BatchMixChocolateIceCreateSerializer
from process_store.views import add_process_store

logger = logging.getLogger(__name__)


@api_view(['POST'])
def batch_mix_create(request):
    try:
        batch_data = request.data.get('batch_data', {})
        ingredients = request.data.get('ingredients', [])

        print(batch_data,'==================inital data')

        # Calculate expiration date
        try:
            exp_days = int(batch_data.get('expDays', 3))
        except ValueError:
            exp_days = 3

        batch_date = timezone.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d').date()
        exp_date = batch_date + timedelta(days=exp_days)

        data = {
            'batchName': batch_data.get('batchName'),
            'batchCode': batch_data.get('batchCode'),
            'batchDate': batch_date,
            'expDate': exp_date,
            'subCategory': batch_data.get('subCategory'),
            'totalVolume': batch_data.get('totalVolume'),
            'ingredients': ingredients
        }

        serializer = BatchMixCreateSerializer(data=data, context={'request': request,"batch":data})

        if serializer.is_valid():
            batch_mix = serializer.save()

            try:
                add_process_store(batch_mix)
                logger.info(f"Process store added for batch mix {batch_mix.id}")
            except Exception as e:
                logger.error(f"Failed to add process store for batch mix {batch_mix.id}: {str(e)}")

            return Response(BatchMixCreateSerializer(batch_mix).data, status=status.HTTP_201_CREATED)

        # If there are errors, format them as specified
        error_message = next(iter(serializer.errors.values()))[0] if serializer.errors else "Validation error"
        return Response({
            "message": error_message,
            "status": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Unexpected error in batch_mix_create")
        return Response({
            "message": "An unexpected error occurred",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def batch_mix_chocolate_icecream_create(request):
    try:
        batch_data = request.data.get('batch_data', {})
        ingredients = request.data.get('ingredients', [])

        # Calculate expiration date
        try:
            exp_days = int(batch_data.get('expDays', 3))
        except ValueError:
            exp_days = 3

        batch_date = timezone.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d').date()
        exp_date = batch_date + timedelta(days=exp_days)

        data = {
            'batchName': batch_data.get('batchName'),
            'batchCode': batch_data.get('batchCode'),
            'batchDate': batch_date,
            'expDate': exp_date,
            'subCategory': batch_data.get('subCategory'),
            'totalVolume': batch_data.get('totalVolume'),
            'ingredients': ingredients
        }

        serializer = BatchMixChocolateIceCreateSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            batch_mix = serializer.save()

            try:
                add_process_store(batch_mix)
                logger.info(f"Process store added for batch mix {batch_mix.id}")
            except Exception as e:
                logger.error(f"Failed to add process store for batch mix {batch_mix.id}: {str(e)}")

            return Response(BatchMixChocolateIceCreateSerializer(batch_mix).data, status=status.HTTP_201_CREATED)

        # If there are errors, format them as specified
        error_message = next(iter(serializer.errors.values()))[0] if serializer.errors else "Validation error"
        return Response({
            "message": error_message,
            "status": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Unexpected error in batch_mix_create")
        return Response({
            "message": "An unexpected error occurred",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# def batch_mix_create(request):
#     try:
#         batch_data = request.data.get('batch_data', {})
#         ingredients = request.data.get('ingredients', [])
#         print(batch_data, "========batch_data")
#         print(ingredients, "ingredients==========dd")
#         try:
#             try:
#                 expDays = int(batch_data.get('expDays'))
#             except Exception as e:
#                 # print(e)
#                 expDays = 3
#
#             expDate = datetime.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d') + datetime.timedelta(
#                 days=expDays)
#
#         except Exception as e:
#             # print(e)
#             expDate = datetime.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d') + datetime.timedelta(days=3)
#
#         data = {
#             'batchName': batch_data.get('batchName'),
#             'batchCode': batch_data.get('batchCode'),
#             'batchDate': batch_data.get('batchDate'),
#             'expDate': expDate.strftime('%Y-%m-%d'),
#             'subCategory': batch_data.get('subCategory'),
#             'totalVolume': batch_data.get('totalVolume'),
#             'ingredients': ingredients
#         }
#
#
#         try:
#             serializer = BatchMixCreateSerializer(data=data, context={'request': request})
#         except Exception as e:
#             pass
#             # print(e)
#         if serializer.is_valid():
#             batch_mix = serializer.save()
#             try:
#                 print("=====================================")
#                 print(batch_mix.id,batch_mix.totalVolume,batch_mix.expDate)
#                 print("=====================================")
#                 process_store_add = add_process_store(batch_mix)
#                 if process_store_add:
#                     print("added to process data -------------------------------------------------------------------")
#                 else:
#                     print("not added to process data ---------------------------------------------------------------")
#
#             except Exception as e:
#                 print(e)
#             return Response(BatchMixCreateSerializer(batch_mix).data, status=status.HTTP_201_CREATED)
#         # If there are errors, format them as you specified
#         error_response = {
#             "message": "Validation error.",
#             "status": status.HTTP_400_BAD_REQUEST
#         }
#         if serializer.errors:
#             # You can customize the message based on the first error or handle multiple errors if needed
#             first_error_message = list(serializer.errors.values())[0][0] if serializer.errors else "Unknown error"
#             error_response["message"] = first_error_message
#             return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
#         return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def batch_mix_detail(request, pk=None):
    if pk is not None:

        try:
            syrup_batch_mix = BatchMix.objects.filter(pk=pk).first()
            # ingredients_in_syrup_batch_mix = BatchMixIngredients.objects.filter(BatchMix=syrup_batch_mix)
        except BatchMix.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # serializer = BatchMixNewDetailsSerializer(syrup_batch_mix)
        serializer = BatchMixSerializer(syrup_batch_mix)
        # print(serializer.data, "serializer.data")
        # ingredient_serializer = SyrupBatchMixIngredientsSerializer(ingredients_in_syrup_batch_mix, many=True)
        # return Response({'batch': serializer.data, 'ingredients': ingredient_serializer.data})
        return Response(serializer.data)
    else:
        try:
            syrup_batch_mix = BatchMix.objects.all()
            # print(syrup_batch_mix, "syrup_batch_mix------------------------get iic")
        except BatchMix.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = GetBatchMixDetailSerializer(syrup_batch_mix, many=True)
        return Response(serializer.data)


from django_filters import rest_framework as filters
# ===================
# Define the filter class
import django_filters

class BatchMixFilter(django_filters.FilterSet):
    class Meta:
        model = BatchMix
        fields = ['batchName', 'batchCode', 'batchDate', 'expDate', 'subCategory', 'totalVolume',]


# Create the ListAPIView for listing BatchMix objects
class BatchMixSyrupAndSouceListView(generics.ListAPIView):
    queryset = BatchMix.objects.all()
    serializer_class = GetBatchMixSerializer
    filterset_class = BatchMixFilter
    filter_backends = (filters.DjangoFilterBackend,)
    ordering_fields = '__all__'
    ordering = ['id']  # Default ordering

    def list(self, request, *args, **kwargs):
        # Filter by subCategory names
        filtered_queryset = self.get_queryset().filter(subCategory__category__name__in=["Souce", "Syrup"], is_deleted=False)

        # Serialize and return the data
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)

class BatchMixIcCreamMixListView(generics.ListAPIView):
    queryset = BatchMix.objects.all()
    serializer_class = GetBatchMixSerializer
    filterset_class = BatchMixFilter
    filter_backends = (filters.DjangoFilterBackend,)
    ordering_fields = '__all__'

    def list(self, request, *args, **kwargs):
        # Filter by subCategory names
        filtered_queryset = self.get_queryset().filter(subCategory__category__name__in=["Ice Cream Mix",], is_deleted=False)

        # Serialize and return the data
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)
#
class BatchMixChoclateIcCreamMixListView(generics.ListAPIView):
    queryset = BatchMix.objects.all()
    serializer_class = GetBatchMixSerializer
    filterset_class = BatchMixFilter
    filter_backends = (filters.DjangoFilterBackend,)
    ordering_fields = '__all__'
    #
    def list(self, request, *args, **kwargs):
        # Filter by subCategory names
        filtered_queryset = self.get_queryset().filter(subCategory__category__name__in=["Chocolate Ice Cream"], is_deleted=False)

        # Serialize and return the data
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)

# =================update==================

def convert_to_mm_dd_yy(date_str):
    """Convert various date formats to 'MM DD YY' format."""
    # Define possible date formats
    date_formats = ['%Y-%m-%d', '%y%m%d', '%m/%d/%Y', '%m-%d-%Y']

    for fmt in date_formats:
        try:
            # Parse the date string
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime('%m %d %y')  # Convert to 'MM DD YY' format
        except ValueError:
            continue  # Try the next format

    raise ValueError("Invalid date format")  # If no formats matched
# <editor-fold desc="update batch mix and update process store">
@api_view(['PUT'])
def batch_mix_update_view(request, pk):

    try:
        # First try to get the existing batch mix
        try:
            batch_mix = BatchMix.objects.get(pk=pk)
        except BatchMix.DoesNotExist:
            return Response({
                "message": "BatchMix not found",
                "status": status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)

        batch_data = request.data.get('batch_data', {})
        ingredients = request.data.get('ingredients', [])

        # Prepare data for update
        data = {
            'batchName': batch_data.get('batchName'),
            'batchCode': batch_data.get('batchCode'),
            'batchDate': batch_mix.batchDate,
            'expDate': batch_mix.expDate,
            'subCategory': batch_data.get('subCategory'),
            'totalVolume': batch_data.get('totalVolume'),
            'ingredients': ingredients
        }
        serializer = BatchMixUpdateSerializer(
            batch_mix,
            data=data,
            partial=True,
            context={'request': request,"ingredients_data":ingredients,"batch":data}
        )

        if serializer.is_valid():
            updated_batch_mix = serializer.save()


            # Return the updated data
            return Response({
                "data": BatchMixUpdateSerializer(updated_batch_mix).data,
                "message": "Batch mix updated successfully",
                "status": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        # If there are validation errors, format them as specified
        error_message = next(iter(serializer.errors.values()))[0] if serializer.errors else "Validation error"
        return Response({
            "message": error_message,
            "status": status.HTTP_400_BAD_REQUEST
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Log the full exception for debugging
        logger.exception("Unexpected error in batch_mix_update_view")
        return Response({
            "message": "An unexpected error occurred",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['PUT'])
# def batch_mix_update_view(request, pk):
#     try:
#         batch_mix = BatchMix.objects.get(pk=pk)
#     except BatchMix.DoesNotExist:
#         return Response({'error': 'BatchMix not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     try:
#         print(request.data,'===============request data ')
#         batch_data = request.data.get('batch_data', {})
#         ingredients = request.data.get('ingredients', [])
#         try:
#             expDays = int(batch_data.get('expDays', 3))
#         except ValueError:
#             expDays = 3
#
#         batch_date = timezone.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d').date()
#         exp_date = batch_date + timedelta(days=expDays)
#
#
#         data = {
#             'batchName': batch_data.get('batchName'),
#             'batchCode': batch_data.get('batchCode'),
#             'batchDate': batch_data.get('batchDate'),
#             'expDate': exp_date,
#             'subCategory': batch_data.get('subCategory'),
#             'totalVolume': batch_data.get('totalVolume'),
#             'ingredients': ingredients
#         }
#         print(batch_mix,'--------------------dtaa send ing data')
#         serializer = BatchMixUpdateSerializer(batch_mix, data=data, partial=True,context={'request': request})
#         if serializer.is_valid():
#             updated_batch_mix = serializer.save()
#
#             return Response(BatchMixUpdateSerializer(updated_batch_mix).data, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# </editor-fold>


class BatchMixUpdateView(generics.UpdateAPIView):
    queryset = BatchMix.objects.all()  # Queryset to retrieve BatchMix instances
    serializer_class = BatchMixUpdateExpiredSerializer  # Specify the serializer to use

    def patch(self, request, *args, **kwargs):
        # Use the default update behavior provided by UpdateAPIView
        return self.update(request, *args, **kwargs)
# =================================get ==========================

from rest_framework import generics

class BatchMixWithTemplateDetail(generics.RetrieveAPIView):
    queryset = BatchMix.objects.filter(is_deleted=False)
    serializer_class = BatchMixIcreamGetTemplateDetailsSerializer
