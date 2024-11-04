
from rest_framework import serializers

from accounts.models import UserBase
from inventory.models import GoodsReturnNote, Material, Type, Vendor, VendorContactPersons, SecurityNote
from inventory.utils import generate_grn_number


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'
        depth = 1
class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'
        depth = 1



class GETgrnSerializer(serializers.ModelSerializer):
    material = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    damaged_images = serializers.SerializerMethodField()
    rejected_images = serializers.SerializerMethodField()
    # invoice_image = serializers.SerializerMethodField()
    def get_material(self, obj):
        return MaterialSerializer(obj.materialName).data or {}
    def get_type(self, obj):
        return TypeSerializer(obj.typeName).data

    def get_damaged_images(self, obj):
        request = self.context.get('request')  # Get the request from the serializer's context
        return [
            request.build_absolute_uri(obj.damageImage1.url) if obj.damageImage1 else None,
            request.build_absolute_uri(obj.damageImage2.url) if obj.damageImage2 else None,
            request.build_absolute_uri(obj.damageImage3.url) if obj.damageImage3 else None,
        ]

    def get_rejected_images(self, obj):
        request = self.context.get('request')  # Get the request from the serializer's context
        return [
            request.build_absolute_uri(obj.rejectedImage1.url) if obj.rejectedImage1 else None,
            request.build_absolute_uri(obj.rejectedImage2.url) if obj.rejectedImage2 else None,
            request.build_absolute_uri(obj.rejectedImage3.url) if obj.rejectedImage3 else None,
        ]

    # def get_invoice_image(self,obj):
    #     request = self.context.get('request')
    #     return request.build_absolute_uri(obj.invoiceImage.url)

    class Meta:
        model = GoodsReturnNote
        # fields = ['GRNnumber',
        #           'mfgDate',
        #           'billNo',
        #           'batchNumber',
        #           'receivedDate',
        #           'measure',
        #           'unitSize',
        #           'quantityPerPackage',
        #           'unitPrice',
        #           'damage',
        #           'description',
        #           'materialName',
        #           'typeName',
        #           'vendor',
        #           'receivedBy',
        #           'packageType',
        #           'totalQuantity',
        #           'totalPrice',
        #           'approvedQuantity',
        #           'damage',
        #           'damageSubject',
        #           'vehicleNumber',
        #           'damageImage1',
        #           'damageImage2',
        #           'damageImage3',
        #           'invoiceImage',
        #           'qualityCheckBy',
        #           'rejectedCompletely',
        #           'expDate',
        #           'grnMaterialDescription'
        #           ]
        # rejectedCompletely,rejectedQuantity,rejectedReason,rejectedImage1,rejectedImage2,rejectedImage3
        fields= '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Customize materialName representation
        representation['materialName'] = instance.materialName.materialName

        # Customize typeName representation
        representation['typeName'] = instance.typeName.typeName

        # Customize vendor representation
        representation['vendor'] = instance.vendor.enterpriseName
        representation['vendor_id'] = instance.vendor.id

        try:
            if f"{instance.qualityCheckBy.first_name}" is not None:
                representation[
                    'qualityCheckBy'] = f"{instance.qualityCheckBy.first_name} {instance.qualityCheckBy.last_name}"
            else:
                representation['qualityCheckBy'] = None
        except:
            representation['qualityCheckBy'] = None

        # Customize receivedBy representation
        try:
            representation[
                'receivedBy'] = f"{instance.receivedBy.first_name} {instance.receivedBy.last_name}"
        except:
            representation['receivedBy'] = None

        return representation


# <editor-fold desc="grn create ">
class POSTgrnSerializer(serializers.ModelSerializer):
    GRNnumber=serializers.CharField(max_length=10, min_length=10,required=False)
    class Meta:
        model = GoodsReturnNote
        fields='__all__'

    def create(self, validated_data):
        # print(validated_data,'============formart')
        # # Get the images from context or default to empty dicts
        damageImages_instance = self.context.get('damaged', {})
        rejectedImages_instance = self.context.get('rejected', {})

        print(damageImages_instance, '==========ddddddddddddddddd')
        print(rejectedImages_instance, '==========dreeeeej')


        try:
            type_name=Type.objects.get(id=validated_data['typeName'].id)
        except:
            return serializers.ValidationError({"message":"type does not exist"})
        try:
            material_name=Material.objects.get(id=validated_data['materialName'].id)
        except:
            return serializers.ValidationError({"message":"material does not exist"})
        try:
            vendor_name=Vendor.objects.get(id=validated_data['vendor'].id)
        except:
            return serializers.ValidationError({"message":"material does not exist"})

        print("helo,'==============create",type_name,material_name,vendor_name)

        print("grn not exist")
        grn_number = generate_grn_number()
        grn= GoodsReturnNote.objects.create(GRNnumber=grn_number,**validated_data)

        print("save,'-----------------hfhfk-----here ",grn.id)


        for i in range(1, 4):  # Assuming there are up to 3 damage images
            image_key = f'damageImage{i}'
            new_image = damageImages_instance.get(image_key)
            if new_image:  # Only set if the new image is not None
                setattr(grn, image_key, new_image)
                print(grn.id, '===============grn  imghse ')

        for i in range(1, 4):  # Assuming there are up to 3 rejected images
            image_key = f'rejectedImage{i}'
            new_image = rejectedImages_instance.get(image_key)
            if new_image:  # Only set if the new image is not None
                setattr(grn, image_key, new_image)
                print(grn.id, '===============grn  imgh s')

        # Save any changes made to the existing instance (if not created)
        grn.save()
        print(grn.id,'===============grn  imgh ')


        return validated_data
# </editor-fold>





# =========================
from rest_framework import serializers

class MaterialSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class TypeSerializerUpdate(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = '__all__'

class SecurityNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityNote
        fields = '__all__'



# ===============================

class GoodsReturnNoteSerializer(serializers.ModelSerializer):
    materialName = MaterialSerializerUpdate(required=False)
    typeName = TypeSerializerUpdate(required=False)
    vendor = VendorSerializer(required=False)
    receivedBy = UserBaseSerializer(required=False)
    qualityCheckBy = UserBaseSerializer(required=False)
    securityNote = SecurityNoteSerializer(required=False)

    damaged =serializers.DictField()
    rejected =serializers.DictField()
    invoice=serializers.ImageField(write_only=True)
    def validate(self, attrs):
        print(attrs,'=========ss=====')

        return attrs

    class Meta:
        model = GoodsReturnNote
        fields='__all__'

    def update(self, instance, validated_data):
        print(validated_data, '============validate')
        # # Get the images from context or default to empty dicts
        damageImages_instance = self.context.get('damaged', {})
        rejectedImages_instance = self.context.get('rejected', {})

        print(damageImages_instance, '==========ddddddddddddddddd')
        print(rejectedImages_instance, '==========dreeeeej')
        # Dynamically assign damage images to the instance fields if they are not None
        for i in range(1, 4):  # Assuming there are up to 3 damage images
            image_key = f'damageImage{i}'
            new_image = damageImages_instance.get(image_key)
            if new_image is not None:  # Only set if the new image is not None
                setattr(instance, image_key, new_image)

        # Dynamically assign rejected images to the instance fields if they are not None
        for i in range(1, 4):  # Assuming there are up to 3 rejected images
            image_key = f'rejectedImage{i}'
            new_image = rejectedImages_instance.get(image_key)
            if new_image is not None:  # Only set if the new image is not None
                setattr(instance, image_key, new_image)
        # Update instance attributes with validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the instance and handle exceptions
        try:
            instance.save()
        except Exception as e:
            raise serializers.ValidationError(f"Failed to save GoodsReturnNote: {str(e)}")

        return instance


from rest_framework import serializers
from process_store.models import ProcessStore

class ProcessStoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessStore
        fields = ['batch', 'quantity', 'expDate', 'currentQuantity', 'created', 'updated']
        depth=2

