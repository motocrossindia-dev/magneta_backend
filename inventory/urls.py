from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from inventory.view.BatchMix import batch, batch_detail, batch_mix_templates
# from inventory.view.BatchMix import batch_mix_templates, get_batch_mix_template
# from inventory.view.BatchMixCategories import batch_mix_categories
# from inventory.view.BatchMixSubCategories import batch_mix_sub_categories
from inventory.view.GRN import grn, receiveGRN, grn_track, \
    GoodsReturnNoteExpireView, GrnUpdateView, grn_create
from inventory.view.Material import material
from inventory.view.Security import security, delete_security_note
from inventory.view.Store import get_store_data
from inventory.view.SubType import subTypes
# from inventory.view.SyrupBatchMix import syrup_batch_mix_detail, syrup_batch_mix_create, syrup_batch_mix_update
from inventory.view.Type import types
from inventory.view.Vendor import vendor

app_name = 'inventory'

urlpatterns = [
    path('vendor/', vendor, name='vendor'),
    path('materials/', material, name='material'),
    path('types/', types, name='types'),
    path('subTypes/', subTypes, name='types'),
    path('grn/', grn, name='grn'),
    # path('grn_create/', grn_create, name='grn_create'),
    path('grn/<str:grn>/', grn, name='grn'),
    path('grn_track/<str:GRNnumber>', grn_track, name='grn_track'),
    # path('receive_grn/<str:GRNnumber>/', receiveGRN, name='receiveGRN'),
    path('receive_grn/', receiveGRN, name='receiveGRN'),
    path('security/', security, name='security'),
    path('security/<int:pk>/', delete_security_note, name='security'),

    # path('batch/', batch, name='batch'),
    # path('batch_detail/<int:pk>/', batch_detail, name='batch_detail'),
    path('get_store_data/', get_store_data, name='get_store_data'),


    path('goods-return-note/<int:pk>/', GrnUpdateView.as_view(), name='grn-update'),

    path('goods-return-notes/<int:id>/update_and_check_expiration/',
         GoodsReturnNoteExpireView.as_view(),
         name='goods-return-note-update'),



    # new
    # path('batch_mix_sub_categories/', batch_mix_sub_categories, name='get_batch_mix_sub_categories'),
    # path('batch_mix_sub_categories/<int:pk>/', batch_mix_sub_categories, name='update_batch_mix_sub_categories'),
    #
    # path('batch_mix_categories/', batch_mix_categories, name='get_batch_mix_categories'),
    # path('batch_mix_categories/<int:pk>/', batch_mix_categories, name='update_batch_mix_categories'),

    # batchMix Templates
    # path('batch_mix_template/', batch_mix_templates, name='batch_mix_templates'),
    # path('batch_mix_template/<int:pk>/', get_batch_mix_template, name='get_batch_mix_template'),

    # path('syrup_batch_mix/', syrup_batch_mix_create, name='syrup_batch_mix_create'),
    # path('get_syrup_batch_mix/', syrup_batch_mix_detail, name='syrup_batch_mix_detail'),
    # path('get_syrup_batch_mix/<int:pk>/', syrup_batch_mix_detail, name='syrup_batch_mix_detail'),
    # path('syrup_batch_mix/<int:pk>/update/', syrup_batch_mix_update, name='syrup_batch_mix_update'),
]
