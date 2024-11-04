from rest_framework import serializers

from inventory.models import Material, SubType, Type


class GetSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=SubType
        fields='__all__'
class GetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Type
        fields='__all__'
class GETmaterialSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    subType = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ['id', 'materialName', 'materialDescription', 'type', 'subType', 'created', 'updated']

    def get_type(self, obj):
        if obj.type:
            return GetTypeSerializer(obj.type).data
        return None

    def get_subType(self, obj):
        if obj.subType:
            return GetSubTypeSerializer(obj.subType).data
        return None
    # type = GetTypeSerializer(read_only=True)
    # subtype = serializers.SerializerMethodField(source='get_subtype')
    # def get_subtype(self, obj):
    #     subtype = GetSubTypeSerializer(obj.subType).data
    #     return subtype
    # class Meta:
    #     model = Material
    #     fields = ['id', 'materialName', 'materialDescription', 'type','subtype']
    #     read_only_fields = ['id']


class POSTMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields ='__all__'

    def validate(self, data):
        materialName = data.get('materialName')
        # type = data.get('type')
        # if Material.objects.filter(materialName=materialName, type=type).exists():
        if Material.objects.filter(materialName=materialName).exists():
            raise serializers.ValidationError("This material name already exists.")
        return data

    def create(self, validated_data):
        print(validated_data,'--------------------data`1')
        try:
            material=Material.objects.get(materialName=validated_data['materialName'],type=validated_data['type'])
        except:
            material=Material.objects.create(**validated_data)

        return validated_data
