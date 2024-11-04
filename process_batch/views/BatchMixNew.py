import datetime

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from process_batch.serializers.BatchMixCreateNew import BatchMixNewSerializer
from process_store.views import add_process_store

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import datetime
#
# @api_view(['POST'])
# def batch_mix_create_new(request):
#     batch_data = request.data.get('batch_data', {})
#     ingredients = request.data.get('ingredients', [])
#
#     # Set default expiration days if not provided or invalid
#     try:
#         exp_days = int(batch_data.get('expDays', 3))
#     except ValueError:
#         exp_days = 3
#
#     # Calculate expiration date
#     try:
#         batch_date = datetime.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d')
#         exp_date = batch_date + datetime.timedelta(days=exp_days)
#     except ValueError:
#         exp_date = datetime.datetime.strptime(batch_data.get('batchDate', datetime.datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d') + datetime.timedelta(days=3)
#
#     # Prepare data for serializer
#     data = {
#         'batchName': batch_data.get('batchName'),
#         'batchCode': batch_data.get('batchCode'),
#         'batchDate': batch_data.get('batchDate'),
#         'expDate': exp_date.strftime('%Y-%m-%d'),
#         'subCategory': batch_data.get('subCategory'),
#         'totalVolume': batch_data.get('totalVolume'),
#         'ingredients': ingredients
#     }
#
#     # Serialize data
#     serializer = BatchMixNewSerializer(data=data, context={'request': request})
#
#     if serializer.is_valid():
#         batch_mix = serializer.save()
#         process_store_add = add_process_store(batch_mix)
#         if process_store_add:
#             print("Added to process data")
#         else:
#             print("Not added to process data")
#         return Response(BatchMixNewSerializer(batch_mix).data, status=status.HTTP_201_CREATED)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#


@api_view(['POST'])
def batch_mix_create_new(request):
    try:
        batch_data = request.data.get('batch_data', {})
        ingredients = request.data.get('ingredients', [])
        print(request.data, "batch_data")
        try:
            try:
                expDays = int(batch_data.get('expDays'))
            except Exception as e:
                print(e)
                expDays = 3

            expDate = datetime.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d') + datetime.timedelta(
                days=expDays)

        except Exception as e:
            print(e)
            expDate = datetime.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d') + datetime.timedelta(days=3)

        data = {
            'batchName': batch_data.get('batchName'),
            'batchCode': batch_data.get('batchCode'),
            'batchDate': batch_data.get('batchDate'),
            'expDate': expDate.strftime('%Y-%m-%d'),
            'subCategory': batch_data.get('subCategory'),
            'totalVolume': batch_data.get('totalVolume'),
            'ingredients': ingredients
        }
        try:
            serializer = BatchMixNewSerializer(data=data, context={'request': request})
        except Exception as e:
            print(e)
        if serializer.is_valid():
            batch_mix = serializer.save()
            try:
                print("===================foiyguigyiu ==================")
                print(batch_mix.id,batch_mix.totalVolume,batch_mix.expDate)
                print("=====================================")
                process_store_add = add_process_store(batch_mix)
                if process_store_add:
                    print("added to process data -----ghefytrfen new --------------------------------------------------------------")
                else:
                    print("not added to process data -----------ccc----------------------------------------------------")

            except Exception as e:
                print(e)
            return Response(BatchMixNewSerializer(batch_mix).data, status=status.HTTP_201_CREATED)
        # If there are errors, format them as you specified
        error_response = {
            "message": "Validation error.",
            "status": status.HTTP_400_BAD_REQUEST
        }
        if serializer.errors:
            # You can customize the message based on the first error or handle multiple errors if needed
            first_error_message = list(serializer.errors.values())[0][0] if serializer.errors else "Unknown error"
            error_response["message"] = first_error_message
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

