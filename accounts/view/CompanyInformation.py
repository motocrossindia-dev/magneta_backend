from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission
from accounts.models import CompanyInformation

import logging

from accounts.serializers.CompanyInformationSerializer import GETcompanyInformationSerializer, \
    PATCHcompanyInformationSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
def company_information(request, pk=None):
    if request.method == 'GET' and pk is None:
        try:
            company_info = CompanyInformation.objects.all().first()
            serializer = GETcompanyInformationSerializer(company_info, many=False)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: company_information " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH' and pk is not None:
        try:
            company_info = get_object_or_404(CompanyInformation, pk=pk)
            serializer = PATCHcompanyInformationSerializer(instance=company_info, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data={"msg": "Company information updated successfully"}, status=status.HTTP_200_OK)
            else:
                logger.error("Error in company_information: ", str(serializer.errors))
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: company_information " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in company_information: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
