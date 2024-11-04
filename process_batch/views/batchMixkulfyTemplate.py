from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from inventory.models import Material
from process_batch.models.batchMixkulfyTemplate import BatchMixkulfyTemplate
from process_batch.serializers.batchMixkulfyTemplateSerializer import GETBatchMixkulfyTemplateSerializer, \
    BatchMixkulfyTemplateSerializer
from process_store.models import ProcessStore


@api_view(['GET', 'POST', 'PATCH'])

def batch_mix_kulfy_templates(request):
    if request.method == 'GET':
        try:
            batch_mix_templates = BatchMixkulfyTemplate.objects.filter(is_deleted=False).prefetch_related(
                'ingredients')


            # print(batch_mix_templates, "batch_mix_templates")
            serializer = GETBatchMixkulfyTemplateSerializer(batch_mix_templates, many=True)
            # print(serializer.data, "serializer.data ============================================")

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            # print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'POST':

        print(request.data,'---------------------------------------main now template batch mix start')
        batch_data = request.data.get('batch_data', {})
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
        #         ======================================
        print(batch_data, "============1============batch_data")
        print(batch_products, "=========2===========batch_products")

        # Combine the data into a single dictionary
        combined_data = {
            'batchName': batch_data.get('batchName'),
            'batchCode': batch_data.get('batchCode'),
            'subCategory': int(batch_data.get('subCategory')),
            'batchDate': batch_data.get('batchDate'),
            'expDays': batch_data.get('expDays'),
            'ingredients': batch_products,
        }

        serializer = BatchMixkulfyTemplateSerializer(data=combined_data)
        if serializer.is_valid():
            batchName = serializer.validated_data['batchName']
            if BatchMixkulfyTemplate.objects.filter(batchName__iexact=batchName).exists():
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
            template = BatchMixkulfyTemplate.objects.get(pk=template_id)
            serializer = BatchMixkulfyTemplateSerializer(template, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(serializer.errors, "serializer.errors in batch mix templates patch")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_batch_mix_kulfy_template(request, pk):
    if request.method == 'GET':
        try:
            get_batch_mix_templates = (BatchMixkulfyTemplate.objects.filter
                                   (pk=pk,is_deleted=False).prefetch_related('ingredients').first())
            if get_batch_mix_templates is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = GETBatchMixkulfyTemplateSerializer(get_batch_mix_templates)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ===============================
