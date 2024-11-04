# views.py

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.exceptions import ValidationError
# # from inventory.models import BatchMixCategory
# # from inventory.serializers.BatchMixSerializer import BatchMixCategorySerializer
# from django.db.utils import IntegrityError


# @api_view(['GET', 'POST', 'PATCH'])
# def batch_mix_categories(request, pk=None):
#     if request.method == 'GET':
#         try:
#             categories = BatchMixCategory.objects.filter(is_deleted=False)
#             serializer = BatchMixCategorySerializer(categories, many=True)
#             return Response({"data": serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     elif request.method == 'POST':
#         serializer = BatchMixCategorySerializer(data=request.data)
#         if serializer.is_valid():
#             name = serializer.validated_data['name']
#             if BatchMixCategory.objects.filter(name__iexact=name).exists():
#                 return Response({'error': 'Category with this name already exists.'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#             try:
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             except IntegrityError:
#                 return Response({'error': 'Error saving category'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'PATCH':
#         print(pk)
#         try:
#             category = BatchMixCategory.objects.get(pk=pk)
#         except BatchMixCategory.DoesNotExist:
#             return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = BatchMixCategorySerializer(category, data=request.data, partial=True)
#         if serializer.is_valid():
#             name = serializer.validated_data.get('name', None)
#             if name and BatchMixCategory.objects.filter(name__iexact=name).exclude(pk=pk).exists():
#                 return Response({'error': 'Category with this name already exists.'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#             try:
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             except IntegrityError:
#                 return Response({'error': 'Error updating category'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def create_batch_mix_category(request):
#     serializer = BatchMixCategorySerializer(data=request.data)
#     if serializer.is_valid():
#         name = serializer.validated_data['name']
#         if BatchMixCategory.objects.filter(name__iexact=name).exists():
#             return Response({'error': 'Category with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except IntegrityError:
#             return Response({'error': 'Error saving category'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# @api_view(['PATCH'])
# def update_batch_mix_category(request, pk):
#     try:
#         category = BatchMixCategory.objects.get(pk=pk)
#     except BatchMixCategory.DoesNotExist:
#         return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     serializer = BatchMixCategorySerializer(category, data=request.data, partial=True)
#     if serializer.is_valid():
#         name = serializer.validated_data.get('name', None)
#         if name and BatchMixCategory.objects.filter(name__iexact=name).exclude(pk=pk).exists():
#             return Response({'error': 'Category with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except IntegrityError:
#             return Response({'error': 'Error updating category'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
