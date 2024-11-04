from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from inventory.models import Material
from process_batch.models.BatchMixIceCream import BatchMixIceCreamTemplate, BatchMixIceCreamTemplateIngredients
from process_batch.serializers.batchMixIccreamTemplateSerializer import GETBatchMixIceCreamTemplateSerializer, \
    BatchMixIceCreamTemplateSerializer, BatchMixIceCreamTemplateUpdateSerializer
from process_store.models import ProcessStore


@api_view(['GET', 'POST', 'PATCH'])
def batch_mix_icecream_template(request):
    if request.method == 'GET':
        try:
            batch_mix_templates = BatchMixIceCreamTemplate.objects.filter(is_deleted=False).prefetch_related(
                'ingredients')
            # print(batch_mix_templates, "batch_mix_templates")
            serializer = GETBatchMixIceCreamTemplateSerializer(batch_mix_templates, many=True)
            # print(serializer.data, "serializer.data ============================================")

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            # print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'POST':
        batch_data = request.data.get('batch_data', {})
        print(batch_data,'-----------------data')
        batch_products = request.data.get('batch_products', [])
        for product in batch_products:
            product['object_id'] = product.get('ingredient_id')
            content_type = product.get('content_type')
            if content_type == "RMStore":
                content_type = ContentType.objects.get_for_model(Material)
                product['content_type'] = content_type.pk
            elif content_type == "ProcessStore":
                content_type = ContentType.objects.get_for_model(ProcessStore)
                product['content_type'] = content_type.pk
            else:
                print(content_type)
        # print(batch_products, "batch_products")

        # Combine the data into a single dictionary
        combined_data = {
            'batchName': batch_data.get('batchName'),
            'batchCode': batch_data.get('batchCode'),
            'subCategory': int(batch_data.get('subCategory')),
            'batchDate': batch_data.get('batchDate'),
            'expDays': batch_data.get('expDays'),
            'ingredients': batch_products,
             'milk_fat_percentage':float(batch_data.get('milk_fat_percentage')),
             'milk_snf_percentage':float(batch_data.get('milk_snf_percentage')),
             'batch_fat_percentage':float(batch_data.get('batch_fat_percentage')),
             'batch_snf_percentage':float(batch_data.get('batch_snf_percentage')),
             'cream_percentage':float(batch_data.get('cream_percentage')),
             'butter_percentage':float(batch_data.get('butter_percentage')),
             'smp_snf_percentage':float(batch_data.get('smp_snf_percentage')),
             'standard_converstion_factor':float(batch_data.get('standard_converstion_factor')),
        }

        serializer = BatchMixIceCreamTemplateSerializer(data=combined_data)
        if serializer.is_valid():
            batchName = serializer.validated_data['batchName']
            if BatchMixIceCreamTemplate.objects.filter(batchName__iexact=batchName).exists():
                return Response({'error': 'Template with this name already exists.'},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'error': 'Error saving template'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(serializer.errors, "serializer.errors in batch mix templates")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        try:
            template_id = request.data.get('template_id')
            template = BatchMixIceCreamTemplate.objects.get(pk=template_id)
            serializer = BatchMixIceCreamTemplateSerializer(template, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(serializer.errors, "serializer.errors in batch mix templates patch")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_batch_mix_icecream_template(request, pk):
    if request.method == 'GET':
        try:
            print(pk,'-===========id')
            get_batch_mix_templates = (BatchMixIceCreamTemplate.objects.filter(pk=pk,is_deleted=False).prefetch_related('ingredients').first())
            print(get_batch_mix_templates,'----------------temp')
            if get_batch_mix_templates is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = GETBatchMixIceCreamTemplateSerializer(get_batch_mix_templates)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e,'==============here nnot gett')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ===============================


# =========================update=====================================
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType


@api_view(['PUT'])
def update_batch_mix_ice_cream_template(request, template_id):
    try:
        batch_template = BatchMixIceCreamTemplate.objects.get(id=template_id)
    except BatchMixIceCreamTemplate.DoesNotExist:
        return Response({'error': 'Batch Mix Ice Cream Template not found.'}, status=status.HTTP_404_NOT_FOUND)

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
        'milk_fat_percentage': batch_data.get('milk_fat_percentage'),
        'milk_snf_percentage': batch_data.get('milk_snf_percentage'),
        'batch_fat_percentage': batch_data.get('batch_fat_percentage'),
        'batch_snf_percentage': batch_data.get('batch_snf_percentage'),
        'cream_percentage': batch_data.get('cream_percentage'),
        'butter_percentage': batch_data.get('butter_percentage'),
        'smp_snf_percentage': batch_data.get('smp_snf_percentage'),
        'standard_converstion_factor': batch_data.get('standard_converstion_factor'),
        'ingredients': ingredients,
    }

    serializer = BatchMixIceCreamTemplateUpdateSerializer(batch_template, data=combined_data, partial=True)

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
                        BatchMixIceCreamTemplateIngredients.objects.create(
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