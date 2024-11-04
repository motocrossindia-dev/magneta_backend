import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import UserBase
from sales.serializers.SalesLoginSerializer import SalesLoginSerializer

logger = logging.getLogger("magneta_logger")


@api_view(['POST'])
@permission_classes([AllowAny])
def login_distributor(request):
    if request.method == 'POST':
        login_from = request.data.get('login_from')
        try:
            serializer = SalesLoginSerializer(data=request.data, login_from=login_from, context={'request': request})

            if serializer.is_valid():
                # get_role, get_permissions = user_permissions(user_id=serializer.data['id'])
                updated_data = dict(serializer.data)
                distributor = UserBase.objects.get(id=serializer.data['id'])
                updated_data['role'] = distributor.role.role

                # print(get_role, get_permissions)
                data = {"msg": "Logged in Successfully.", "user": updated_data}

                return Response(data=data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Error in login_user: {str(serializer.errors)}")
                return Response(data={"error": serializer.errors}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Exception: login_user " + str(e))
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in login_user: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
