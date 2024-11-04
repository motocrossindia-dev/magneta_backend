import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsDistributorPermission
from advertisements.models import Banner
from advertisements.serializers.BannerSerializer import GETbannerSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDistributorPermission])
@permission_classes([AllowAny])
@authentication_classes([JWTAuthentication])
def banners(request):
    if request.method == 'GET':
        try:
            banner = Banner.objects.filter(is_active=True)
            serializer = GETbannerSerializer(banner, many=True)
            return Response(data={"banners": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data={"Exception:", str(e)})
    elif request.method == 'POST':
        try:
            serializer = GETbannerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data={"message": "Banner created successfully!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={"Exception": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
