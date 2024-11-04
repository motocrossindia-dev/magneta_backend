import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.CustomPermissions import IsManagerOrDistributorPermission
from accounts.models import UserBase, Role
from accounts.serializers.AccountRegisterSerializer import POSTaccountRegisterSerializer, \
    PATCHaccountRegisterSerializer, ChangeProfilePictureSerializer
# from accounts.serializers.RoleSerializer import GETrolesSerializer
from utils.states_cities import get_all_states, states_data

logger = logging.getLogger("magneta_logger")


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated, IsManagerOrDistributorPermission])
@authentication_classes([JWTAuthentication])
def account_register(request, pk=None):
    # in GET method, return list of roles from hard tuple of roles
    # if request.method == 'GET' and pk is None and request.user.is_manager:
    #     try:
    #         roles = Role.objects.all()
    #         serializer = GETrolesSerializer(roles, many=True)
    #         return Response(data={"roles": serializer.data})
    #     except Exception as e:
    #         logger.error("Exception: account_register " + str(e))
    #         return Response(data={"Exception": str(e)})

    if request.method == 'POST' and (request.user.is_manager or request.user.is_distributor):
        try:
            # request_data = request.data.copy()
            aadhar = request.data.get('aadhar', '000000000000')
            pan = request.data.get('pan', 'XXXXX0000X')
            gst = request.data.get('gst', '29XXXXX0000X0Z0')
            request_data = {
                'aadhar': aadhar,
                'pan': pan,
                'gst': gst,
                'last_name': request.data.get('last_name'),
                'phone_number': request.data.get('phone_number'),
                'enterprise_name': request.data.get('enterprise_name'),
                'emergency_phone_number': request.data.get('emergency_phone_number'),
                'Address': request.data.get('Address'),
                'state': request.data.get('state'),
                'city': request.data.get('city'),
                'pincode': request.data.get('pincode'),
                'password': request.data.get('password'),
                'otp': request.data.get('otp'),
                'date_of_birth': request.data.get('date_of_birth'),
                'is_retailer': request.data.get('is_retailer'),
                'is_distributor': request.data.get('is_distributor', False),
                'is_manager': request.data.get('is_manager', False),
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

                # adding role to user
                try:
                    role = Role.objects.get(role=request.data.get('role'))
                except:
                    role, created = Role.objects.get_or_create(role='Staff')

                request_data['role'] = role
                new_user.role = role
                new_user.save()

                return Response(data={"msg": "Account registered successfully. "
                                             "Please Check your mail for account Activation",
                                      "data": serializer.data})
            elif serializer.errors:
                logger.error(f"Error in account_register: {str(serializer.errors)}")
                if serializer.errors.get('phone_number'):
                    return Response(data={"error": "Phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: account_register " + str(e))
            return Response(data={"Exception": str(e)})

    elif request.method == 'PATCH' and pk is not None:
        try:
            request_data = request.data.copy()

            aadhar = request_data.get('aadhar')
            pan = request_data.get('pan')
            gst = request_data.get('gst')

            account = UserBase.objects.get(id=pk)
            try:
                if aadhar == '' or aadhar is None:
                    request_data['aadhar'] = account.aadhar
            except:
                pass
            try:
                if pan == '' or pan is None:
                    request_data['pan'] = account.pan
            except:
                pass
            try:
                if gst == '' or gst is None:
                    request_data['gst'] = account.gst
            except:
                pass
            serializer = PATCHaccountRegisterSerializer(instance=account, data=request_data, partial=True,
                                                        context={"request": request})
            if serializer.is_valid():
                serializer.save()
                profile_image_data = request.FILES.get('profile_picture')
                if profile_image_data:

                    serializer = ChangeProfilePictureSerializer(instance=account,
                                                                data={'profile_picture': profile_image_data},
                                                                partial=True)
                    if serializer.is_valid():
                        serializer.save()
                    elif serializer.errors:
                        return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                return Response(data={"msg": "User data updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Exception: account_register " + str(e))
            return Response(data={"Exception": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.error("Invalid request method or missing user ID")
        return Response(data={"error": "Invalid request method or missing user ID"}, status=status.HTTP_400_BAD_REQUEST)
