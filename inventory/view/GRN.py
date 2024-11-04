import logging

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsStoreManagerPermission
from inventory.models import GoodsReturnNote, SecurityNote
from inventory.serializers.GRNserializer import POSTgrnSerializer, GETgrnSerializer, GoodsReturnNoteSerializer, \
    ProcessStoreSerializer
from inventory.utils import generate_grn_number
from process_batch.models.BatchMix import BatchMixIngredients
from process_store.models import ProcessStore

logger = logging.getLogger("magneta_logger")


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated, IsStoreManagerPermission])
# @permission_classes([IsAuthenticated, IsManagerPermission])
@parser_classes([MultiPartParser, FormParser])
@authentication_classes([JWTAuthentication])
def grn(request,grn=None):
    user = request.user
    if request.method == "GET":
        try:
            grns = GoodsReturnNote.objects.all().order_by('-id')
            serializer = GETgrnSerializer(grns, many=True,context={'request': request})
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: vendor " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        #     serializer = POSTgrnSerializer(data=grn_data,context={"request": request})
        #     if serializer.is_valid():
        #         instance_data=serializer.save()
        #         security_note_id = grn_data.get('security_note_id', None)
        #         if security_note_id:
        #             try:
        #                 security_note = get_object_or_404(SecurityNote, pk=security_note_id)
        #                 security_note.is_converted_to_grn = True
        #                 security_note.securityNote = security_note_id
        #                 security_note.save()
        #             except Exception as e:
        #                 logger.error("Exception" + str(e))
        #
        #         return Response(data={"msg": "GRN created Successfully"}, status=status.HTTP_200_OK)
        #     elif serializer.errors:
        #         logger.error("Error in grn: ", str(serializer.errors))
        #         return Response(data={"error": serializer.errors},
        #                         status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     logger.error("Exception: grn " + str(e))
        #     return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        #
    elif request.method in ["POST"]:
        try:
            grn_data = request.data
            #
            # print(grn_data,'===================data first')

            damage = {}
            reject = {}
            damage['damageImage1'] = request.data.get('damageImages[0]')
            damage['damageImage2'] = request.data.get('damageImages[1]')
            damage['damageImage3'] = request.data.get('damageImages[2]')

            reject['rejectedImage1'] = request.data.get('rejectedImages[0]')
            reject['rejectedImage2'] = request.data.get('rejectedImages[1]')
            reject['rejectedImage3'] = request.data.get('rejectedImages[2]')
            #
            # print(damage, '----------dama')
            # print(reject, '----------reject')

            # Initialize serializer with the incoming data
            serializer = POSTgrnSerializer(data=grn_data, context={"request": request,
                                                                   'damaged': damage,
                'rejected': reject})

            if serializer.is_valid():
                # Save the GRN data
                serializer.save()

                # If security_note_id is provided, update the related SecurityNote object
                security_note_id = grn_data.get('security_note_id', None)
                print(security_note_id,'===================data here ')
                if security_note_id:
                    try:
                        security_note = get_object_or_404(SecurityNote, pk=security_note_id)
                        security_note.is_converted_to_grn = True
                        security_note.save()
                        print(security_note,'=========security')
                    except Exception as e:
                        logger.error("Exception in SecurityNote update: " + str(e))

                # Return success response
                return Response(data={"msg": "GRN created successfully"}, status=status.HTTP_201_CREATED)
            else:
                # Handle invalid serializer errors
                logger.error("Error in POST GRN: " + str(serializer.errors))
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other exceptions
            logger.error("Exception in POST GRN: " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         # Retrieve the existing GRN to update
    #         grn_instance = get_object_or_404(GoodsReturnNote, GRNnumber=grn)
    #
    #         serializer = GoodsReturnNoteSerializer(grn_instance, partial=(request.method == "PUT"))
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(data={"msg": "GRN updated  successfully"}, status=status.HTTP_200_OK)
    #         else:
    #             logger.error("Error in grn update: " + str(serializer.errors))
    #             return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     except Exception as e:
    #         logger.error("Exception in GRN update: " + str(e))
    #         return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    # elif request.method in ["PATCH"]:
    #     try:
    #         # Retrieve the existing GRN to update
    #         grn_instance = get_object_or_404(GoodsReturnNote, GRNnumber=grn)
    #
    #         serializer = GoodsReturnNoteSerializer(grn_instance, partial=(request.method == "PATCH"))
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(data={"msg": "GRN updated successfully"}, status=status.HTTP_200_OK)
    #         else:
    #             logger.error("Error in grn update: " + str(serializer.errors))
    #             return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     except Exception as e:
    #         logger.error("Exception in GRN update: " + str(e))
    #         return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        try:
            # Retrieve the GRN to delete
            grn_instance = get_object_or_404(GoodsReturnNote, GRNnumber=grn)
            grn_instance.delete()
            return Response(data={"msg": "GRN deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception in GRN deletion: " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in orders: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStoreManagerPermission])
@authentication_classes([JWTAuthentication])
def receiveGRN(request):
    GRNnumber=request.data.get('GRNnumber')
    if not GRNnumber:
        return Response(data={"error": "GRN number is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        grn = get_object_or_404(GoodsReturnNote, GRNnumber=GRNnumber)
        grn.receivedBy = request.user
        grn.save()
        return Response(data={"data": "data"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Exception: grn " + str(e))
        return Response(data={"data": f"Exception: grn  + {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, authentication_classes

logger = logging.getLogger(__name__)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
def grn_track(request, GRNnumber):
    logger.info(f"Attempting to track GRN/batch number: {GRNnumber}")

    try:
        # Check if GRNnumber matches GoodsReturnNote
        logger.debug("Querying GoodsReturnNote")
        grn = GoodsReturnNote.objects.get(GRNnumber=GRNnumber)
        logger.info(f"Found matching GRN: {grn}")
        serializer = GETgrnSerializer(grn,context={"request":request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        logger.info(f"No matching GRN found for {GRNnumber}, checking ProcessStore")

        try:
            # If not found, check in ProcessStore by batch code
            logger.debug("Querying ProcessStore")
            process_store = ProcessStore.objects.filter(batch__batchCode__icontains=GRNnumber).first()
            logger.info(f"Found matching ProcessStore: {process_store}")
            serializer = ProcessStoreSerializer(process_store)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            logger.warning(f"No matching ProcessStore found for batch code: {GRNnumber}")
            return Response({"error": "No matching GRN or batch found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error querying ProcessStore: {str(e)}", exc_info=True)
            return Response({"error": "Error querying ProcessStore"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error querying GoodsReturnNote: {str(e)}", exc_info=True)
        return Response({"error": "Error querying GoodsReturnNote"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(["GET"])
# @authentication_classes([JWTAuthentication])
# def grn_track(request,GRNnumber):
#     try:
#         grn = GoodsReturnNote.objects.filter(GRNnumber=GRNnumber).first()
#         serializer = GETgrnSerializer(grn)
#         return Response( serializer.data, status=status.HTTP_200_OK)
#     except Exception as e:
#         logger.error("Exception: grn " + str(e))
#         return Response(data={"data": f"Exception: grn  + {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
# =======================================================update -----------------------request

from rest_framework.generics import UpdateAPIView
from django.shortcuts import get_object_or_404
# Helper function to get the URL as a string
def get_image_url(image):
    if isinstance(image, str):
        return image
    elif hasattr(image, 'url'):  # Check if it's an InMemoryUploadedFile
        return image.url
    return None
class GrnUpdateView(UpdateAPIView):
    queryset = GoodsReturnNote.objects.all()
    serializer_class = GoodsReturnNoteSerializer
    lookup_field = 'pk'

    def patch(self, request, pk, *args, **kwargs):
        """
        Handles PATCH requests to partially update a GoodsReturnNote instance.
        """
        print(request.data,'===========request data')
        instance = get_object_or_404(GoodsReturnNote, pk=pk)

        damage={}
        reject={}
        damage['damageImage1']=request.data.get('damageImages[0]')
        damage['damageImage2']=request.data.get('damageImages[1]')
        damage['damageImage3']=request.data.get('damageImages[2]')

        reject['rejectedImage1']=request.data.get('rejectedImages[0]')
        reject['rejectedImage2']=request.data.get('rejectedImages[1]')
        reject['rejectedImage3']=request.data.get('rejectedImages[2]')

        print(damage,'----------dama')
        print(reject,'----------reject')

        # Serialize the incoming data, bind it to the instance (partial=True)
        serializer = GoodsReturnNoteSerializer(
            instance,
            data=request.data,
            partial=True,
            context={
                "request": request,
                'damaged': damage,
                'rejected': reject
            }
        )

        # Validate and save if valid
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)


@api_view(["POST"])
def grn_create(request):
    try:
        grn_data = request.data
        # Initialize serializer with the incoming data
        serializer = POSTgrnSerializer(data=grn_data, context={"request": request})

        if serializer.is_valid():
            # Save the GRN data
            serializer.save()

            # If security_note_id is provided, update the related SecurityNote object
            security_note_id = grn_data.get('security_note_id', None)
            if security_note_id:
                try:
                    security_note = get_object_or_404(SecurityNote, pk=security_note_id)
                    security_note.is_converted_to_grn = True
                    security_note.save()
                except Exception as e:
                    logger.error("Exception in SecurityNote update: " + str(e))

            # Return success response
            return Response(data={"msg": "GRN created successfully"}, status=status.HTTP_201_CREATED)
        else:
            # Handle invalid serializer errors
            logger.error("Error in POST GRN: " + str(serializer.errors))
            return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle any other exceptions
        logger.error("Exception in POST GRN: " + str(e))
        return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT'])
# def goods_return_note_update(request, GRNnumber=None):
#     if request.method == "PUT":
#         return update_goods_return_note(request, GRNnumber)
#
#
# def update_goods_return_note(request, grn):
#     try:
#         # Try to find the GoodsReturnNote with the given pk
#         grn = GoodsReturnNote.objects.filter(GRNnumber=grn).first()
#
#         if grn:
#             # If found, update the GRN
#             return update_grn(grn, request)
#         else:
#             # If not found, try to find a matching ProcessStore based on batch__batchCode
#             return update_process_store(request, grn)
#
#     except Exception as e:
#         logger.error("Exception: updating GRN or ProcessStore " + str(e))
#         return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#
# def update_grn(grn, request):
#     grn_data = request.data.copy()
#
#     handle_image_upload(request, grn_data, 'damageImage', ['damageImage1', 'damageImage2', 'damageImage3'])
#     handle_image_upload(request, grn_data, 'rejectedImages', ['rejectedImage1', 'rejectedImage2', 'rejectedImage3'])
#
#     if 'invoiceImage' in request.FILES:
#         grn_data['invoiceImage'] = request.FILES.get('invoiceImage')
#
#     serializer = POSTgrnSerializer(grn, data=grn_data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         update_security_note(grn_data.get('security_note_id'))
#         return Response(data={"msg": "GRN updated Successfully"}, status=status.HTTP_200_OK)
#     else:
#         logger.error("Error in updating GRN: " + str(serializer.errors))
#         return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#
# #
# def update_process_store(request, batch_code):
#     try:
#         # Try to find ProcessStore with matching batch__batchCode
#         process_store = ProcessStore.objects.filter(batch__batchCode=batch_code).first()
#
#         if process_store:
#             process_data = request.data.copy()
#             serializer = ProcessStoreSerializer(process_store, data=process_data, partial=True)
#
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(data={"msg": "ProcessStore updated Successfully"}, status=status.HTTP_200_OK)
#             else:
#                 logger.error("Error in updating ProcessStore: " + str(serializer.errors))
#                 return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#
#         else:
#             return Response(data={"error": "ProcessStore with batch code not found"}, status=status.HTTP_404_NOT_FOUND)
#
#     except Exception as e:
#         logger.error("Exception: updating ProcessStore " + str(e))
#         return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# def handle_image_upload(request, data, field_name, image_fields):
#     images = request.FILES.getlist(field_name)
#     for i, image_field in enumerate(image_fields):
#         if i < len(images):
#             data[image_field] = images[i]
#
#
# def update_security_note(security_note_id):
#     if security_note_id:
#         try:
#             security_note = get_object_or_404(SecurityNote, pk=security_note_id)
#             security_note.is_converted_to_grn = True
#             security_note.securityNote = security_note_id
#             security_note.save()
#         except Exception as e:
#             logger.error("Exception in updating security note: " + str(e))

#
# @api_view(['PUT'])
# def goods_return_note_update(request, pk=None):
#     if request.method == "PUT":
#         return update_goods_return_note(request, pk)
#
#
# def update_goods_return_note(request, pk):
#     try:
#         grn = get_object_or_404(GoodsReturnNote, GRNnumber=pk)
#         grn_data = request.data.copy()
#
#         handle_image_upload(request, grn_data, 'damageImage', ['damageImage1', 'damageImage2', 'damageImage3'])
#         handle_image_upload(request, grn_data, 'rejectedImages', ['rejectedImage1', 'rejectedImage2', 'rejectedImage3'])
#
#         if 'invoiceImage' in request.FILES:
#             grn_data['invoiceImage'] = request.FILES.get('invoiceImage')
#
#         serializer = POSTgrnSerializer(grn, data=grn_data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             update_security_note(grn_data.get('security_note_id'))
#             return Response(data={"msg": "GRN updated Successfully"}, status=status.HTTP_200_OK)
#         else:
#             logger.error("Error in updating grn: " + str(serializer.errors))
#             return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         logger.error("Exception: updating grn " + str(e))
#         return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#
# def handle_image_upload(request, data, field_name, image_fields):
#     images = request.FILES.getlist(field_name)
#     for i, image_field in enumerate(image_fields):
#         if i < len(images):
#             data[image_field] = images[i]
#
#
# def update_security_note(security_note_id):
#     if security_note_id:
#         try:
#             security_note = get_object_or_404(SecurityNote, pk=security_note_id)
#             security_note.is_converted_to_grn = True
#             security_note.securityNote = security_note_id
#             security_note.save()
#         except Exception as e:
#             logger.error("Exception in updating security note: " + str(e))

from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class GoodsReturnNoteExpireView(generics.UpdateAPIView):
    queryset = GoodsReturnNote.objects.all()
    serializer_class = GoodsReturnNoteSerializer
    lookup_field = 'id'

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        grn = self.get_object()
        # Check if the GRN inventory is not expired (invert the condition if necessary)
        if not grn.inventory_is_expired():
            return Response({"message": "GRN is not expired. Cannot proceed."}, status=status.HTTP_400_BAD_REQUEST)

        if grn.is_expired:
            return Response({"message": "GRN is already expired."}, status=status.HTTP_400_BAD_REQUEST)

        update_result = self.update_batch_mix(grn)

        return Response({
            "message": f"GRN {grn.GRNnumber} marked as expired.",
            "update_result": update_result
        })

    def update_batch_mix(self, grn):
        quantity_to_deduct = grn.totalQuantity or 0

        if quantity_to_deduct <= 0:
            logger.warning(f"No quantity to deduct for GRN {grn.GRNnumber}")
            return {"status": "No deduction", "reason": "Total quantity is zero or negative"}

        try:
            # Fetch all BatchMixIngredients
            batch_mix_ingredients = BatchMixIngredients.objects.all()
            logger.info(f"Found {len(batch_mix_ingredients)} BatchMixIngredients to process.")

            updates = []
            for bmi in batch_mix_ingredients:
                # Use get_grnlist_as_dict to retrieve unique GRN
                grn_dict = self.get_grnlist_as_dict(bmi)
                unique_grn = next(iter(grn_dict.values()), None)

                if unique_grn is None:
                    logger.warning(f"No unique GRN found for BatchMixIngredient {bmi.id}.")
                    continue

                # Check if the unique GRN matches the one we're processing
                logger.info(
                    f"Checking BatchMixIngredient {bmi.id}: unique GRN {unique_grn}, target GRN {grn.GRNnumber}.")

                if unique_grn == grn.GRNnumber:

                    ingredient_quantity = bmi.quantity
                    print(ingredient_quantity,'==============quntity',unique_grn)
                    # Calculate the difference
                    difference = quantity_to_deduct - ingredient_quantity

                    # Check if the difference is valid
                    if difference < 0:
                        logger.warning(
                            f"Calculated difference for GRN {grn.GRNnumber} is negative: {difference}. Not updating.")
                        continue

                    # Update the GoodsReturnNote
                    update_grn_result = GoodsReturnNote.objects.filter(GRNnumber=unique_grn).update(
                        totalQuantity=difference, is_expired=True)
                    logger.info(f"Updated GoodsReturnNote for GRN {grn.GRNnumber}: {update_grn_result} rows affected.")

                    # logger.info(f"Updated BatchMix {bmi.SyrupBatchMix.id}: {update_grn_result} rows affected.{update_grn_result.first().is_expired} status")

                    updates.append({
                        "status": "Success",
                        "grn_quantity": quantity_to_deduct,
                        "ingredient_quantity": ingredient_quantity,
                        "difference": difference,
                        "unique_grn": unique_grn
                    })

                    break  # Stop after processing one matching BatchMixIngredient

            if not updates:
                logger.warning("No updates were made. No matching BatchMixIngredients found.")
                return {"status": "Failed", "reason": "No BatchMixIngredients processed"}

            return updates[0]  # Return the first (and only) successful result

        except Exception as e:
            logger.error(f"Error processing BatchMix for GRN {grn.GRNnumber}: {str(e)}")
            return {"status": "Error", "reason": str(e)}

    def get_grnlist_as_dict(self, obj):
        # Check if grnlist is None or empty
        if not hasattr(obj, 'grnlist') or obj.grnlist is None or not obj.grnlist:
            return {i: x.batch.batchCode for i, x in enumerate(obj.ingredient_process_store.all())}

        if isinstance(obj.grnlist, list):
            unique_grns = set()

            for grn in obj.grnlist:
                if isinstance(grn, dict) and 'grn' in grn:
                    unique_grns.add(grn['grn'])
                elif isinstance(grn, str):
                    unique_grns.add(grn)

            unique_grn = next(iter(unique_grns), None)
            return {0: unique_grn} if unique_grn else {}

        elif isinstance(obj.grnlist, str):
            grnlist = [grn.strip() for grn in obj.grnlist.split(',') if grn.strip()]
            unique_grn = next(iter(set(grnlist)), None)
            return {0: unique_grn} if unique_grn else {}

        return {}

