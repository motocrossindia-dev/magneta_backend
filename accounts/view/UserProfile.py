from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerPermission, IsManagerOrDistributorPermission
from accounts.models import UserBase, Role
from accounts.serializers.ProfileSerializer import GETUserProfileSerializer
import logging

logger = logging.getLogger("magneta_logger")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def user_profile(request, pk=None):
    if request.method == 'GET' and pk is None:
        try:
            user = UserBase.objects.filter(is_superuser=False)
            serializer = GETUserProfileSerializer(user, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: user_profile " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET' and pk is not None:
        try:
            user = UserBase.objects.get(id=pk)
            serializer = GETUserProfileSerializer(user)
            print(serializer.data)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: user_profile " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
@api_view(['GET', 'POST'])
def search_profile(request):
    if request.method == 'GET':
        try:
            cities = UserBase.objects.values_list('city', flat=True).distinct().exclude(city__isnull=True)
            return Response(data={"cities": cities}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: search_profile " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        try:
            is_manager = request.data.get('is_manager', 'false').lower() == 'true'
            is_distributor = request.data.get('is_distributor', 'false').lower() == 'true'
            is_retailer = request.data.get('is_retailer', 'false').lower() == 'true'

            filter_query = Q()
            city = request.data.get('city')
            if request.data.get('city') != '':
                filter_query &= Q(city=city)
            if request.data.get('is_manager') != '':
                filter_query &= Q(is_manager=is_manager)
            if request.data.get('is_distributor') != '':
                filter_query &= Q(is_distributor=is_distributor)
            if request.data.get('is_retailer') != '':
                filter_query &= Q(is_retailer=is_retailer)

            filter_query &= Q(is_superuser=False)
            filtered_data = UserBase.objects.filter(filter_query)

            if not filtered_data:
                return Response(data={"data": ["no data found"]}, status=status.HTTP_200_OK)
            serializer = GETUserProfileSerializer(filtered_data, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception: search_profile " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("search_profile Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated, IsManagerPermission])
@authentication_classes([JWTAuthentication])
@api_view(['POST'])
def update_user_role(request):
    try:
        if request.method == 'POST':
            user_id = request.data.get('user_id')
            role = request.data.get('role')
            user = UserBase.objects.get(id=user_id)
            role_instance = Role.objects.get(id=role)
            user.role = role_instance
            user.save()
            serializer = GETUserProfileSerializer(user)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Exception: update_user_role " + str(e))
        return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
