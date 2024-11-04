from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (Category, Subcategory, Product, ProductImage,
                     ProductSize, ProductFlavour, ProductSpecification)


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductSizeInline(admin.TabularInline):
    model = ProductSize


class ProductFlavourInline(admin.TabularInline):
    model = ProductFlavour


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['id', 'name', 'description']


@admin.register(Subcategory)
class SubcategoryAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['id', 'name', 'category']


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['id', 'product_name', 'subcategory', 'carton_size', 'price', 'is_active', 'product_barcode',
                    'carton_barcode', 'gst', 'factory_gst', 'factory_sale',
                    'distributor_margin_rate', 'distributor_margin_price', 'distributor_gst', 'distributor_sale',
                    'retailer_margin_rate', 'retailer_margin_price', 'retailer_gst', 'retailer_sale',
                    'retailer_base_price', 'retailer_base_gst', 'mrp']
    inlines = [ProductImageInline]
    # inlines = [ProductImageInline, ProductSizeInline, ProductFlavourInline, ProductSpecificationInline]


@admin.register(ProductImage)
class ProductImageAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['product', 'product_images']


@admin.register(ProductSize)
class ProductSizeAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['size_name', 'product', 'size_volume']


@admin.register(ProductFlavour)
class ProductFlavourAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['flavour_name', 'product']


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['specification_name', 'product']
