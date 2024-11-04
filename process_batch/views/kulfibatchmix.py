import datetime

from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from process_batch.models.batchMixkulfyTemplate import BatchMixkulfyTemplateIngredients, BatchMixkulfyTemplate
from process_batch.serializers.kulfiBatchMixSerializer import *
from process_store.views import add_process_store


@api_view(['POST'])
def kulfi_batch_mix_create(request):
    try:
        batch_data = request.data.get('batch_data', {})
        ingredients = request.data.get('ingredients', [])
        # print(request.data, "batch_data")
        try:
            try:
                expDays = int(batch_data.get('expDays'))
            except Exception as e:
                # print(e)
                expDays = 3

            expDate = datetime.datetime.strptime(batch_data.get('batchDate'), '%Y-%m-%d') + datetime.timedelta(
                days=expDays)

        except Exception as e:
            # print(e)
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
            serializer = BatchMixCreateSerializer(data=data, context={'request': request})
        except Exception as e:
            print(e)
        if serializer.is_valid():
            batch_mix = serializer.save()
            try:
                # print("=====================================")
                print(batch_mix.id,batch_mix.totalVolume,batch_mix.expDate)
                # print("=====================================")
                process_store_add = add_process_store(batch_mix)
                if process_store_add:
                    print("added to process data -------------------------------------------------------------------")
                else:
                    print("not added to process data ---------------------------------------------------------------")

            except Exception as e:
                print(e)
            return Response(BatchMixCreateSerializer(batch_mix).data, status=status.HTTP_201_CREATED)
        if serializer.errors:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===============================================================================

from django_filters import rest_framework as filters
# ===================
# Define the filter class
import django_filters

class BatchMixFilter(django_filters.FilterSet):
    class Meta:
        model = BatchMix
        fields = ['batchName', 'batchCode', 'batchDate', 'expDate', 'subCategory', 'totalVolume',]

class KulfiBatchMixList(generics.ListAPIView):
    queryset = BatchMix.objects.all()
    serializer_class=BatchMixSerializer
    filterset_class = BatchMixFilter
    filter_backends = (filters.DjangoFilterBackend,)
    ordering_fields = '__all__'
    ordering = ['id']  # Default ordering

    def list(self, request, *args, **kwargs):
        # Filter by subCategory names
        filtered_queryset = self.get_queryset().filter(subCategory__category__name__in=["Kulfi",], is_deleted=False)

        # Serialize and return the data
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)


#
class KulfiBatchMixDetail(generics.RetrieveAPIView):
    queryset = BatchMix.objects.all()
    serializer_class = BatchMixSerializer


@api_view(['PATCH'])
def kulfi_batch_mix_update(request, pk):
    try:
        syrup_batch_mix = BatchMix.objects.get(pk=pk)
    except BatchMix.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BatchMixSerializer(syrup_batch_mix, data=request.data, partial=True)
    if serializer.is_valid():
        syrup_batch_mix = serializer.save()
        # Handle ingredients update if needed
        ingredients_data = request.data.get('ingredients', [])
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            if ingredient_id:
                try:
                    ingredient = BatchMixIngredients.objects.get(id=ingredient_id)
                    ingredient_serializer = BatchMixIngredientsSerializer(ingredient, data=ingredient_data,
                                                                               partial=True)
                    if ingredient_serializer.is_valid():
                        ingredient_serializer.save()
                    else:
                        return Response(ingredient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except BatchMixIngredients.DoesNotExist:
                    return Response({'detail': f'Ingredient with id {ingredient_id} not found.'},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                ingredient_data['template'] = syrup_batch_mix.pk
                ingredient_serializer = BatchMixIngredientsSerializer(data=ingredient_data)
                if ingredient_serializer.is_valid():
                    ingredient_serializer.save()
                else:
                    return Response(ingredient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========================update=======


from django.db import transaction, IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType


@api_view(['PUT'])
def kulfi_update_batch_mix_template(request, template_id):
    try:
        batch_template = BatchMixkulfyTemplate.objects.get(id=template_id)
    except BatchMixkulfyTemplate.DoesNotExist:
        return Response({'error': 'Batch Mix Template not found.'}, status=status.HTTP_404_NOT_FOUND)

    batch_data = request.data.get('batch_data', {})
    batch_products = request.data.get('batch_products', [])

    # Prepare ingredients data
    ingredients = []
    for product in batch_products:
        content_type_str = product.get('content_type')
        if content_type_str == "RMStore":
            content_type = ContentType.objects.get_for_model(Material)
        elif content_type_str == "ProcessStore":
            content_type = ContentType.objects.get_for_model(ProcessStore)
        else:
            return Response({'error': f'Invalid content type: {content_type_str}'}, status=status.HTTP_400_BAD_REQUEST)

        ingredients.append({
            'id': product.get('id'),  # Include this for existing ingredients
            'object_id': product.get('ingredient_id'),
            'content_type': content_type_str,
            'type': content_type_str,
            'lowerLimit': product.get('lowerLimit', 0),
            'percentage': product.get('percentage', 0),
            'upperLimit': product.get('upperLimit', 0),
        })

    # Combine the data
    combined_data = {
        'batchName': batch_data.get('batchName'),
        'batchCode': batch_data.get('batchCode'),
        'subCategory': batch_data.get('subCategory'),
        'expDays': batch_data.get('expDays'),
        'ingredients': ingredients,
    }

    serializer = BatchMixKulfiTemplateUpdateSerializer(batch_template, data=combined_data, partial=True)

    if serializer.is_valid():
        try:
            with transaction.atomic():
                updated_template = serializer.save()

                # Handle ingredients
                existing_ingredients = {i.id: i for i in batch_template.ingredients.all()}

                for ingredient_data in ingredients:
                    ingredient_id = ingredient_data.get('id')
                    if ingredient_id and ingredient_id in existing_ingredients:
                        # Update existing ingredient
                        ingredient = existing_ingredients[ingredient_id]
                        for attr, value in ingredient_data.items():
                            if attr != 'id' and attr != 'content_type':
                                setattr(ingredient, attr, value)
                        ingredient.content_type = ContentType.objects.get_for_model(
                            Material if ingredient_data['type'] == 'RMStore' else ProcessStore)
                        ingredient.save()
                        del existing_ingredients[ingredient_id]
                    else:
                        # Create new ingredient
                        BatchMixkulfyTemplateIngredients.objects.create(
                            template=updated_template,
                            content_type=ContentType.objects.get_for_model(
                                Material if ingredient_data['type'] == 'RMStore' else ProcessStore),
                            **{k: v for k, v in ingredient_data.items() if k != 'content_type'}
                        )

                # Delete any remaining existing ingredients
                for ingredient in existing_ingredients.values():
                    ingredient.delete()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)