import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsStoreManagerPermission
from inventory.models import Vendor, SecurityNote
from inventory.serializers.SecuritySerializer import GETSecurityNoteSerializer

logger = logging.getLogger("magneta_logger")


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsStoreManagerPermission])
@authentication_classes([JWTAuthentication])
def security(request):
    if request.method == "GET":
        try:
            security_objects = SecurityNote.objects.filter(is_converted_to_grn=False)
            serializer = GETSecurityNoteSerializer(security_objects, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: security " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "POST":
        try:
            vendor_id = request.data.get('vendor')
            vehicleNo = request.data.get('vehicleNumber')
            billNo = request.data.get('billNo')

            # Fetch the vendor object
            vendor = Vendor.objects.get(id=vendor_id)

            # Create the SecurityNote object
            security_note = SecurityNote.objects.create(
                vendor=vendor,
                vehicleNo=vehicleNo,
                billNo=billNo
            )
            security_note.invoiceImage = request.data.get('invoiceImage')
            security_note.save()

            return JsonResponse({"message": "Security note created successfully", "security_note_id": security_note.id},
                                status=status.HTTP_201_CREATED)
        except Vendor.DoesNotExist:
            logger.error("Vendor not found")
            return Response(data={"error": {"vendor": "Vendor not found"}}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error in security: {str(e)}")
            return Response(data={"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.error("Error in security: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsStoreManagerPermission])
@authentication_classes([JWTAuthentication])
def delete_security_note(request, pk):
    try:
        security_note = get_object_or_404(SecurityNote, pk=pk)
        security_note.delete()
        return Response({"message": "Security note deleted successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in delete_security_note: {str(e)}")
        return Response(data={"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
