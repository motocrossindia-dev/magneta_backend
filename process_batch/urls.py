from django.urls import path

from process_batch.views.BatchMixNew import batch_mix_create_new
from process_batch.views.batchMix import batch_mix_create, batch_mix_detail, \
    BatchMixIcCreamMixListView, BatchMixSyrupAndSouceListView, BatchMixChoclateIcCreamMixListView, \
    batch_mix_update_view, BatchMixUpdateView, BatchMixWithTemplateDetail, batch_mix_chocolate_icecream_create, \
    batch_mix_chocolate_icecream_batchmix_update_view
from process_batch.views.batchMixChocolateIceCreamTemplate import batch_mix_chocolate_ice_cream_templates, \
    get_batch_mix_chocolate_ice_cream_template, update_batch_chocolate_ice_cream_mix_template
from process_batch.views.batchMixIcecreamTemplate import batch_mix_icecream_template, get_batch_mix_icecream_template, \
    update_batch_mix_ice_cream_template
from process_batch.views.batchMixTemplate import batch_mix_templates, get_batch_mix_template, update_batch_mix_template
from process_batch.views.batchMixkulfyTemplate import batch_mix_kulfy_templates, get_batch_mix_kulfy_template
from process_batch.views.categories import batch_mix_sub_categories, batch_mix_categories
from process_batch.views.kulfibatchmix import kulfi_batch_mix_update, kulfi_batch_mix_create, \
    KulfiBatchMixList, KulfiBatchMixDetail, kulfi_update_batch_mix_template

app_name = 'process_batch'

urlpatterns = [
    # Sub Categories
    path('batch_mix_sub_categories/', batch_mix_sub_categories, name='get_batch_mix_sub_categories'),
    path('batch_mix_sub_categories/<int:pk>/', batch_mix_sub_categories, name='update_batch_mix_sub_categories'),

    # Categories
    path('batch_mix_categories/', batch_mix_categories, name='get_batch_mix_categories'),
    path('batch_mix_categories/<int:pk>/', batch_mix_categories, name='update_batch_mix_categories'),

    # Templates For Syrup And Sauce
    # <editor-fold desc="batch mix template create ">
    path('batch_mix_template/', batch_mix_templates, name='batch_mix_templates'),
    # </editor-fold>
    path('batch_mix_template/<int:pk>/', get_batch_mix_template, name='get_batch_mix_template'),
    # Templates For icecream
    path('batch_mix_icecream_template/', batch_mix_icecream_template, name='batch_mix_templates'),
    path('batch_mix_icecream_template/<int:pk>/', get_batch_mix_icecream_template, name='get_batch_mix_template'),

    # <editor-fold desc="batch mix create related ">
    path('batch_mix/', batch_mix_create, name='batch_mix'),

    path('chocolate_ice_cream_batch_mix/', batch_mix_chocolate_icecream_create, name='batch_mix_chocolate_icecream_create'),
    # </editor-fold>

    # <editor-fold desc="ice cream related post  for create ice ">
    path('batch_mix_create/', batch_mix_create_new, name='batch_mix_create'),
    # </editor-fold>

    path('batch_mix_get/', BatchMixSyrupAndSouceListView.as_view(), name='batch_mix'),
    path('batch_mix_get_icecreams/', BatchMixIcCreamMixListView.as_view(), name='batch_mix'),

    path('batch_mix/<int:pk>/', batch_mix_detail, name='batch_mix_new'),
    # path('batch_mix/<int:pk>/delete/', batch_mix_delete, name='batch_mix_delete'),

    # <editor-fold desc="chocolate icecream">
    path('batch_mix_chocolate_ice_cream_template/', batch_mix_chocolate_ice_cream_templates, name='batch_mix_chocolate_ice_cream_templates'),
    # </editor-fold>
    path('batch_mix_chocolate_ice_cream_template/<int:pk>/', get_batch_mix_chocolate_ice_cream_template, name='get_batch_mix_chocolate_ice_cream_template'),
    # </editor-fold>

    # <editor-fold desc="kulfy">
    path('batch_mix_kulfi_template/', batch_mix_kulfy_templates, name='batch_mix_kulfy_templates'),
    # </editor-fold>
    path('batch_mix_kulfi_template/<int:pk>/', get_batch_mix_kulfy_template, name='get_batch_mix_kulfy_template'),
    # </editor-fold>

    #  kulfixbatch mix make
    # <editor-fold desc="batch mix create related">
    path('kulfi_batch_mix/', kulfi_batch_mix_create, name='kulfi_batch_mix'),
    path('kulfi_batch_mix_get/', KulfiBatchMixList.as_view(), name='KulfiBatchMixListURL'),
    path('kulfi_batch_mix/<int:pk>/', KulfiBatchMixDetail.as_view(), name='KulfiBatchMixDetailURL'),
    path('kulfi_batch_mix/<int:pk>/update/', kulfi_batch_mix_update, name='kulfi_batch_mix_update'),
    # </editor-fold>

    path('batch_mix_chocolate_icecreams/',BatchMixChoclateIcCreamMixListView.as_view(), name='bathic_batch_mix_choclate'),

    # ====================edit
    path('batch_mix_template_update/<int:template_id>/', update_batch_mix_template, name='update_batch_mix_template'),

    path('batch_mix_icecream_template_update/<int:template_id>/', update_batch_mix_ice_cream_template,name='update_batch_mix_ice_cream_templateURl'),
    # pass update
    path('batch_mix_chocolate_ice_cream_template_update/<int:template_id>/', update_batch_chocolate_ice_cream_mix_template, name='update_batch_chocolate_ice_cream_mix_template'),

    path('kulfi_batch_mix_template_update/<int:template_id>/', kulfi_update_batch_mix_template, name='kulfi_update_batch_mix_template'),




    # <editor-fold desc="batch mix update">
    path('batch_mix_update/<int:pk>/', batch_mix_update_view, name='batch_mix_update_view'),
    path('batch_mix_chocolate_icecream_update/<int:pk>/', batch_mix_chocolate_icecream_batchmix_update_view, name='batch_mix_chocolate_icecream_batchmix_update_view'),
    # </editor-fold>
    path('batchmix_expired/<int:pk>/', BatchMixUpdateView.as_view(), name='batchmix-update'),

    # <editor-fold desc="ice cream detail">
    path('ice_cream_batchmix_template_details/<int:pk>/', BatchMixWithTemplateDetail.as_view(), name='batchmix-detail'),
    # </editor-fold>
]
