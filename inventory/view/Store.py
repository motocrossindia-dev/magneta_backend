# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from inventory.models import Store
from inventory.serializers.StoreSerializer import StoreSerializer


@api_view(['GET'])
def get_store_data(request):
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)
