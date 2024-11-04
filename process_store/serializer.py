from rest_framework import serializers
from .models import ProcessStore


class ProcessStoreSyrupAndSauceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStore
        fields = ['id','batch', 'quantity', 'expDate', 'currentQuantity']
        depth = 1

# class ProcessStoreSyrupAndSauceSerializer(serializers.ModelSerializer):
#     # materialName = serializers.CharField(source='batch.batchName', read_only=True)
#
#     class Meta:
#         model = ProcessStore
#         fields = ['id','batch', 'quantity', 'expDate', 'currentQuantity']
#         depth = 1
#
    # def get_materialName(self, obj):
    #     return obj.batch.batchName
