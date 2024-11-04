from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from process_batch.models.BatchMix import BatchMix
from .models import ProcessStore
from .serializer import ProcessStoreSyrupAndSauceSerializer


def add_process_store(batch):
    # print("Processing batch:", batch)

    data = {
        'batch': batch.id,
        'quantity': batch.totalVolume,
        'expDate': batch.expDate,
        'currentQuantity': batch.totalVolume
    }
    # print("Data to be processed:", data)
    try:
        batch_get = BatchMix.objects.get(batch=batch)
        # print("Batch found:", batch_get)
    except:
        return Response("Batch not found", status=status.HTTP_404_NOT_FOUND)

    try:
        # print("Trying to retrieve existing ProcessStore")
        # Try to retrieve the existing ProcessStore instance
        process_store = ProcessStore.objects.get(batch=batch_get)
        # If it exists, update the quantity
        process_store.quantity += batch.totalVolume
        process_store.save()
        # print("Updated ProcessStore:", process_store)
    except:
        # If it does not exist, create a new ProcessStore instance
        process_store = ProcessStore.objects.create(quantity=batch.totalVolume,expDate= batch.expDate,
                                                currentQuantity=batch.totalVolume,batch=batch)
        # print("Created new ProcessStore:", process_store)

    return batch


# Add new entry
# @api_view(['POST'])
# def add_process_store(batch):
#     print("added process store when  batch create",batch)
#
#     data = {
#         'batch': batch.id,
#         'quantity': batch.totalVolume,
#         'expDate': batch.expDate,
#         'currentQuantity': batch.totalVolume
#     }
#     print(data)
#     try:
#         process_store=ProcessStore.objects.get(batch=batch)
#     except:
#         process_store=ProcessStore.objects.create(**data)
#
#     print(process_store)
#     process_store.quantity=process_store.quantity+batch.totalVolume
#
#     # serializer = ProcessStoreSyrupAndSauceSerializer(data=data)
#     # if serializer.is_valid():
#     #     serializer.save()
#     #     return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return True

@api_view(['GET'])
def get_process_store(request):
    if request.method == 'GET':
        # Get all ProcessStore instances
        store_syrup_and_sauce = ProcessStore.objects.all()

        # Use a set to track unique batch names and a list comprehension for unique stores
        seen_batches = set()
        unique_stores = [
            store for store in store_syrup_and_sauce
            if store.batch.batchName not in seen_batches and not seen_batches.add(store.batch.batchName)
        ]
        # Serialize the unique results
        serializer = ProcessStoreSyrupAndSauceSerializer(unique_stores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Get all entries
# @api_view(['GET'])
# def get_process_store(request):
#     if request.method == 'GET':
#         store_syrup_and_sauce = ProcessStore.objects.all()
#         serializer = ProcessStoreSyrupAndSauceSerializer(store_syrup_and_sauce, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
