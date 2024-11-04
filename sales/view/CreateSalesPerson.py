import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerOrDistributorPermission
from accounts.models import Role
from accounts.serializers.AccountRegisterSerializer import POSTaccountRegisterSerializer
from sales.models import distributor_sales

logger = logging.getLogger("magneta_logger")


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManagerOrDistributorPermission])
@authentication_classes([JWTAuthentication])
def sales_register(request):
    if request.method == 'POST' and (request.user.is_manager or request.user.is_distributor):
        try:
            aadhar = request.data.get('aadhar', '000000000000')
            pan = request.data.get('pan', 'XXXXX0000X')
            gst = request.data.get('gst', '29XXXXX0000X0Z0')
            request_data = {
                'aadhar': aadhar,
                'pan': pan,
                'gst': gst,
                'last_name': request.data.get('last_name'),
                'phone_number': request.data.get('phone_number'),
                'emergency_phone_number': request.data.get('emergency_phone_number'),
                'Address': request.data.get('Address'),
                'state': request.data.get('state'),
                'city': request.data.get('city'),
                'pincode': request.data.get('pincode'),
                'password': request.data.get('password'),
                'otp': request.data.get('otp'),
                'date_of_birth': request.data.get('date_of_birth'),
                'is_retailer': False,
                'is_distributor': True,
                'is_manager': False,
                'profile_picture': request.FILES.get('profile_picture'),
                'is_active': False if request.data.get('status') == 'false' else True
            }

            if aadhar == '' or aadhar is None:
                request_data['aadhar'] = '000000000000'

            if pan == '' or pan is None:
                request_data['pan'] = 'XXXXX0000X'

            if gst == '' or gst is None:
                request_data['gst'] = '29XXXXX0000X0Z0'

            cust_email = request.data.get('email', None)

            if cust_email is None or cust_email == '':
                try:
                    request_data['email'] = str(request_data.get('phone_number')) + "@magnetaicecream.in"
                    print(request_data['email'])
                except Exception as e:
                    import secrets
                    import string

                    request_data['email'] = str(''.join(
                        secrets.choice(string.ascii_letters + string.digits) for _ in range(6))) + "@magnetaicecream.in"

            else:
                request_data['email'] = cust_email

            cust_first_name = request.data.get('first_name')
            if cust_first_name is None or cust_first_name == '':
                request_data['first_name'] = 'FirstName'
            else:
                request_data['first_name'] = cust_first_name

            serializer = POSTaccountRegisterSerializer(data=request_data, context={'request': request})
            request_data['is_active'] = False if request.data.get('status') == 'false' else True
            if serializer.is_valid():
                new_user = serializer.save()
                role,created=Role.objects.get_or_create(role='sales')
                new_user.role = role
                new_user.save()
                distributor_sales.objects.create(sales_person=new_user, distributor=request.user)

                return Response(data={"msg": "Sales person registered successfully.","data": serializer.data})
            elif serializer.errors:
                logger.error(f"Error in account_register: {str(serializer.errors)}")
                if serializer.errors.get('phone_number'):
                    return Response(data={"error": "Phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: account_register " + str(e))
            return Response(data={"Exception": str(e)})
