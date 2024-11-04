# from datetime import datetime
#
# from django.db import IntegrityError
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
#
# from inventory.models import Batch, BatchIngredients, BatchMixTemplate
# from inventory.serializers.BatchMixSerializer import BatchSerializer, BatchIngredientsSerializer, \
#     GETBatchIngredientsSerializer, BatchMixTemplateSerializer, GetBatchMixTemplateSerializer
#
#
# # @api_view(['GET', 'POST'])
# # def batch(request):
# #     if request.method == 'GET':
# #         batches = Batch.objects.all()
# #         serializer = BatchSerializer(batches, many=True)
# #         return Response(serializer.data)
# #
# #     elif request.method == 'POST':
# #         print(request.data)
# #         data = request.data.get('batch_data')
# #
# #         batch_code = data.get('batchCode')
# #         date = data.get('batchDate', datetime.now().date())
# #
# #         batch_date = datetime.strptime(date, '%Y-%m-%d')
# #         if batch_code and batch_date:
# #             batch_code = f"{batch_code}{batch_date.strftime('%y%m%d')}"
# #             data['batchCode'] = batch_code
# #
# #         print(request.data.get('batch_products'), "batch_ingredients")
# #         data['batch_ingredients'] = request.data.get('batch_products', [])
# #         # data['totalAmount'] = data.get('totalAmount', 0)
# #         # data['totalQuantity'] = data.get('totalQuantity', 0)
# #         print(data)
# #
# #         serializer = BatchSerializer(data=data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(serializer.data, status=status.HTTP_201_CREATED)
# #         print(serializer.errors)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# #
# #
# # @api_view(['GET', 'PUT', 'DELETE'])
# # def batch_detail(request, pk):
# #     try:
# #         getbatch = Batch.objects.get(pk=pk)
# #
# #     except Batch.DoesNotExist:
# #         return Response(status=status.HTTP_404_NOT_FOUND)
# #
# #     if request.method == 'GET':
# #         serializer = BatchSerializer(getbatch)
# #         batch_ingredients = BatchIngredients.objects.filter(batch=getbatch)
# #         batch_serializer = GETBatchIngredientsSerializer(batch_ingredients, many=True)
# #         return Response({"batch": serializer.data, "ingredients": batch_serializer.data})
# #
# #     elif request.method == 'PUT':
# #         serializer = BatchSerializer(getbatch, data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(serializer.data)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# #
# #     elif request.method == 'DELETE':
# #         getbatch.delete()
# #         return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# # =====================================================================================================
# # ============================================ NEW ====================================================
# # =====================================================================================================
# @api_view(['GET', 'POST', 'PATCH'])
# def batch_mix_templates(request):
#     """
#     This template is commonly used for syrup and sauce
#     """
#     if request.method == 'GET':
#         try:
#             batch_mix_templates = BatchMixTemplate.objects.filter(is_deleted=False).prefetch_related('ingredients')
#             serializer = GetBatchMixTemplateSerializer(batch_mix_templates, many=True)
#
#             return Response({"data": serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             print(e)
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     elif request.method == 'POST':
#         batch_data = request.data.get('batch_data', {})
#         batch_products = request.data.get('batch_products', [])
#
#         # Combine the data into a single dictionary
#         combined_data = {
#             'batchName': batch_data.get('batchName'),
#             'batchCode': batch_data.get('batchCode'),
#             'subCategory': int(batch_data.get('subCategory')),
#             'batchDate': batch_data.get('batchDate'),
#             'expDays': batch_data.get('expDays'),
#             'ingredients': batch_products,
#         }
#
#         serializer = BatchMixTemplateSerializer(data=combined_data)
#         if serializer.is_valid():
#             batchName = serializer.validated_data['batchName']
#             if BatchMixTemplate.objects.filter(batchName__iexact=batchName).exists():
#                 return Response({'error': 'Template with this name already exists.'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#             try:
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             except IntegrityError:
#                 return Response({'error': 'Error saving template'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             print(serializer.errors, "serializer.errors")
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'PATCH':
#         try:
#             template_id = request.data.get('template_id')
#             template = BatchMixTemplate.objects.get(pk=template_id)
#             serializer = BatchMixTemplateSerializer(template, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# @api_view(['GET'])
# def get_batch_mix_template(request, pk):
#     if request.method == 'GET':
#         try:
#             print(pk,"pkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
#             batch_mix_templates = BatchMixTemplate.objects.filter(pk=pk, is_deleted=False).prefetch_related(
#                 'ingredients').first()
#             testing=BatchMixTemplate.objects.all()
#             for test in testing:
#                 print(test.id,"test iddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
#             if batch_mix_templates is None:
#                 return Response(status=status.HTTP_404_NOT_FOUND)
#
#             for i in batch_mix_templates:
#                 print(batch_mix_templates[0], "batch_mix_templates ============================================================")
#
#             serializer = GetBatchMixTemplateSerializer(batch_mix_templates)
#             return Response({"data": serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             print(e)
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
