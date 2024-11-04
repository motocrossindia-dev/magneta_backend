import logging
import requests
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from six import text_type

from django.conf import settings
from accounts.serializers.AccountActivateSerializer import POSTAccountActivateSerializer

logger = logging.getLogger("magneta_logger")


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                text_type(user['id']) + text_type(timestamp) +
                text_type(user['is_active'])
        )


account_activation_token = AccountActivationTokenGenerator()


def email_user(user, subject, new_otp):
    message = render_to_string(template_name='account_activation_email.html', context={
        'user': user,
        'otp': new_otp,
    })
    logger.info('before send email')
    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[user['email']],
              fail_silently=False)
    logger.info('after send email')


def send_otp(user):
    phone = "91" + str(user["phone_number"])

    try:
        # =======================================================================
        url = "https://control.msg91.com/api/v5/flow/"
        # payload = {"template_id": "60ffda6d9c235f799241960f",
        #            "recipients": [{"mobiles": phone, "name": name, "otp": otp}]}
        payload = {"template_id": "65bb4b91d6fc0562db225202",
                   "recipients": [{
                       "mobiles": phone,
                       "name": user['name'],
                       "otp": user['otp']
                   }]
                   }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authkey": "112997AX953OZo28W63788920P1"
        }

        response = requests.post(url, json=payload, headers=headers)
        for i in response:
            print(i)
        # =======================================================================
        return True
    except Exception as e:
        return False


@api_view(['POST'])
@permission_classes([AllowAny])
def account_activate(request):
    if request.method == 'POST':
        try:
            request.data.get('phone')
            request.data.get('otp')
            serializer = POSTAccountActivateSerializer(data=request.data, context={'request': request.data})
            if serializer.is_valid():
                return Response(data={"msg": "Account Activated successfully.", "data": serializer.data},
                                status=status.HTTP_200_OK)
            else:
                logger.error("Error in account_activate: {str(serializer.errors)}")
                return Response(data={"Error": serializer.errors})
        except Exception as e:
            logger.error("Exception: account_activate " + str(e))
            return Response(data={"Exception": str(e)})
    else:
        logger.error("Error in account_activate: Invalid request")
        return Response(data={"error": "Invalid request"}, status=status.HTTP_404_NOT_FOUND)
