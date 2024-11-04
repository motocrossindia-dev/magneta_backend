import logging
import random
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import UserBase
from accounts.serializers.OtpSerializer import CheckOtpSerializer
from accounts.view.Account_activate import email_user

logger = logging.getLogger("magneta_logger")


def create_otp():
    try:
        new_otp = "".join(random.choice("0123456789") for _ in range(6))
        return new_otp
    except Exception as e:
        new_otp = "123456"
        return new_otp


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_for_reset_password(request):
    if request.method == 'POST':
        try:
            user = UserBase.objects.filter(email=request.data.get('email')).first()
            new_otp = create_otp()

            if user:
                if not user.is_active:
                    return Response(data={"error": "account is not active"}, status=status.HTTP_400_BAD_REQUEST)
                user.otp = new_otp
                user.save()
                user = {
                    'id': user.id,
                    'is_active': user.is_active,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'name': user.first_name
                }
                subject = 'Reset password of your Account'
                try:
                    email_user(user=user, subject=subject, new_otp=new_otp)
                except Exception as e:
                    logger.error("Error: password_reset----email_user" + str(e))
                # try:
                #     send_otp(user)
                # except Exception as e:
                #     logger.error(f"Error: password_reset----send_otp " + str(e))

                return Response(data={"msg": "Email sent for your account password reset."}, status=status.HTTP_200_OK)
            else:
                return Response(data={"email": "There is no account on this email."},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error: password_reset " + str(e))
            return Response(data={"exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_otp_and_reset_password(request):
    if request.method == 'POST':
        try:
            serializer = CheckOtpSerializer(data=request.data, context={'request': request.data})
            if serializer.is_valid():
                return Response(data={"msg": "Password reset successful."},
                                status=status.HTTP_200_OK)
            elif serializer.errors:
                logger.error("Error in set_reset_password: {str(serializer.errors)}")
                return Response(data={"data": serializer.errors, }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: confirm_otp_and_reset_password " + str(e))
            return Response(data={"exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
