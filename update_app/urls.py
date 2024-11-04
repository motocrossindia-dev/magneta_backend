from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
app_name = 'update_app'

urlpatterns = [
    path('build_number/', views.get_build_number),
    path('partner_build_number/', views.get_partner_build_number),
    path('iphone_build_number/', views.iphone_get_build_number),
    path('iphone_partner_build_number/', views.iphone_get_partner_build_number),
]
