from rest_framework import serializers
from inventory.models import SecurityNote


class GETSecurityNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityNote
        fields = '__all__'
        depth = 1
