from django.urls import path, re_path

from accounts.view.AcountsUserTargetAmountViews import UserTargetAmountViewSet, UsersViewSet
from accounts.view.CompanyInformation import company_information
from accounts.view.DeleteAccount import delete_account, delete_profile_picture
from accounts.view.Login import login_user
from accounts.view.Logout import logout_user
from accounts.view.PasswordReset import send_otp_for_reset_password, confirm_otp_and_reset_password
from accounts.view.Register import account_register
from accounts.view.RoleManager import get_roles, create_role, update_role
from accounts.view.UserBills import user_bills
from accounts.view.UserPermissions import update_user_permissions, get_all_user_permissions, delete_user_permission, \
    get_user_permissions
# from accounts.view.Roles import roles
from accounts.view.UserProfile import user_profile, search_profile, update_user_role

app_name = 'accounts'


from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user_targets', UserTargetAmountViewSet)
router.register(r'users', UsersViewSet)

urlpatterns = [

    path('register/', account_register, name='account_register'),
    path('register/<int:pk>', account_register, name='account_register'),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    re_path('send_otp_for_reset_password/', send_otp_for_reset_password, name='send_otp_for_reset_password'),
    path('confirm_otp_and_reset_password/', confirm_otp_and_reset_password, name='confirm_otp_and_reset_password'),
    re_path(r'^user_profile/(?P<pk>\d+)?$', user_profile, name='user_profile'),
    path('search_profile/', search_profile, name='search_profile'),
    path('delete_account/', delete_account, name='delete_account'),
    path('delete_profile_picture/<int:pk>/', delete_profile_picture, name='delete_profile_picture'),
    path('company_information/', company_information, name='company_information'),
    path('company_information/<int:pk>/', company_information, name='company_information'),
    path('user_bills/<int:pk>/', user_bills, name='user_bills'),
    path('get_all_user_permissions/', get_all_user_permissions, name='get_all_user_permissions'),
    path('get_roles/', get_roles, name='get_roles'),
    path('update_role/<int:role_id>/', update_role, name='update_role'),
    path('create_role/', create_role, name='create_role'),
    path('update_user_role/', update_user_role, name='update_user_role'),

    path('update_user_permissions/', update_user_permissions, name='update_user_permissions'),
    path('delete_user_permissions/<int:permission_id>/', delete_user_permission, name='delete_user_permissions'),
    path('get_user_permissions/<int:user_id>/', get_user_permissions, name='get_user_permissions'),
    path('', include(router.urls)),
]
