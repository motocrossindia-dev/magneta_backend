from django.urls import path, re_path
# from products.view import Products
from products.view.Categories import categories
from products.view.ClaculateMRP import get_mrp
from products.view.Products import products
from products.view.Subcategory import subcategory, get_subcategories_by_category_id

urlpatterns = [
    re_path(r'^categories/(?P<pk>\d+)?$', categories, name='categories'),
    # path('products/', products, name='products'),
    path('subcategories/', subcategory, name='subcategory'),
    re_path(r'^subcategories/(?P<pk>\d+)?$', subcategory, name='subcategory'),
    path('products/', products, name='products'),
    path('products/<int:pk>', products, name='products'),
    path('products/<str:all>', products, name='products'),
    path('products/<str:all>/<int:pk>', products, name='products'),
    re_path(r'^subcategories_by_category/(?P<category_id>\d+)?$', get_subcategories_by_category_id,
            name='get_subcategories_by_category_id'),
    path('calculate_mrp/', get_mrp, name='calculate_mrp'),
]
