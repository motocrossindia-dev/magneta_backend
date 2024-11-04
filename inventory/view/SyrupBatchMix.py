# import datetime
#
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from inventory.models import SyrupBatchMix, SyrupBatchMixIngredients
# from inventory.serializers.SyrupBatchMixSerializer import SyrupBatchMixSerializer, GetSyrupBatchMixSerializer
# from inventory.serializers.SyrupBatchMixSerializer import SyrupBatchMixIngredientsSerializer
# from process_store.models import ProcessStoreSyrupAndSauce
# from process_store.views import add_process_store
#
#
# @api_view(['GET'])
# def syrup_batch_mix_detail(request, pk=None):
#     if pk is not None:
#         try:
#             syrup_batch_mix = SyrupBatchMix.objects.filter(pk=pk).first()
#             # ingredients_in_syrup_batch_mix = SyrupBatchMixIngredients.objects.filter(SyrupBatchMix=syrup_batch_mix)
#         except SyrupBatchMix.DoesNotExist:
#             return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = SyrupBatchMixSerializer(syrup_batch_mix)
#         # ingredient_serializer = SyrupBatchMixIngredientsSerializer(ingredients_in_syrup_batch_mix, many=True)
#         # return Response({'batch': serializer.data, 'ingredients': ingredient_serializer.data})
#         return Response({'batch': serializer.data})
#     else:
#         try:
#             syrup_batch_mix = SyrupBatchMix.objects.all()
#             print(syrup_batch_mix, "syrup_batch_mix")
#         except SyrupBatchMix.DoesNotExist:
#             return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = GetSyrupBatchMixSerializer(syrup_batch_mix, many=True)
#         return Response(serializer.data)
#
#
# @api_view(['POST'])
# def syrup_batch_mix_create(request):
#     try:
#         batch_data = request.data.get('batch_data', {})
#         ingredients = request.data.get('ingredients', [])
#         try:
#             try:
#                 expDays = int(batch_data.get('expDays'))
#             except Exception as e:
#                 print(e)
#                 expDays = 3
#
#             expDate = datetime.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d') + datetime.timedelta(
#                 days=expDays)
#
#         except Exception as e:
#             print(e)
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
#         try:
#             serializer = SyrupBatchMixSerializer(data=data, context={'request': request})
#         except Exception as e:
#             print(e)
#         if serializer.is_valid():
#             syrup_batch_mix = serializer.save()
#             try:
#                 # process_store_syrup_and_sauce=ProcessStoreSyrupAndSauce.objects.create(
#                 #     batch=syrup_batch_mix,
#                 #     quantity=syrup_batch_mix.totalVolume,
#                 #     expDate=syrup_batch_mix.expDate
#                 # )
#                 # process_store_syrup_and_sauce.save()
#                 print("=====================================")
#                 print(syrup_batch_mix.id,syrup_batch_mix.totalVolume,syrup_batch_mix.expDate)
#                 print("=====================================")
#                 process_store_add = add_process_store(syrup_batch_mix)
#                 if process_store_add:
#                     print("added to process data -------------------------------------------------------------------")
#                 else:
#                     print("not added to process data ---------------------------------------------------------------")
#
#             except Exception as e:
#                 print(e)
#             return Response(SyrupBatchMixSerializer(syrup_batch_mix).data, status=status.HTTP_201_CREATED)
#         if serializer.errors:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
# @api_view(['PATCH'])
# def syrup_batch_mix_update(request, pk):
#     try:
#         syrup_batch_mix = SyrupBatchMix.objects.get(pk=pk)
#     except SyrupBatchMix.DoesNotExist:
#         return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
#
#     serializer = SyrupBatchMixSerializer(syrup_batch_mix, data=request.data, partial=True)
#     if serializer.is_valid():
#         syrup_batch_mix = serializer.save()
#         # Handle ingredients update if needed
#         ingredients_data = request.data.get('ingredients', [])
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data.get('id')
#             if ingredient_id:
#                 try:
#                     ingredient = SyrupBatchMixIngredients.objects.get(id=ingredient_id)
#                     ingredient_serializer = SyrupBatchMixIngredientsSerializer(ingredient, data=ingredient_data,
#                                                                                partial=True)
#                     if ingredient_serializer.is_valid():
#                         ingredient_serializer.save()
#                     else:
#                         return Response(ingredient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#                 except SyrupBatchMixIngredients.DoesNotExist:
#                     return Response({'detail': f'Ingredient with id {ingredient_id} not found.'},
#                                     status=status.HTTP_404_NOT_FOUND)
#             else:
#                 ingredient_data['template'] = syrup_batch_mix.pk
#                 ingredient_serializer = SyrupBatchMixIngredientsSerializer(data=ingredient_data)
#                 if ingredient_serializer.is_valid():
#                     ingredient_serializer.save()
#                 else:
#                     return Response(ingredient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)