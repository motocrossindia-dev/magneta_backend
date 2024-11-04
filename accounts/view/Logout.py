import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger("magneta_logger")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def logout_user(request):
    if request.method == 'POST':
        try:
            if request.user:
                refresh_tk = request.data['refresh_token']
                refresh_obj = RefreshToken(refresh_tk)

                refresh_obj.blacklist()
                # outstanding_token = OutstandingToken.objects.filter(token=refresh_tk)
                # outstanding_token.delete()
                logger.info("Exception: logout_user checking logger ")
                return Response(data={"msg": "Logout successfully."}, status=status.HTTP_200_OK)
            else:
                logger.error("error: Trying to logout unknown user.")
                return Response(data={"error": "Unknown user"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error("Exception: logout_user " + str(e))
            return Response(data={"exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Error in logout_user: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)

