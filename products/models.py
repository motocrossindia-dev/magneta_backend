import os
from django.db import models
from django.core.files import File
import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT)
    category = models.CharField(max_length=100)

    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    price = models.FloatField(max_length=10, blank=False, null=False)  # base price
    # min_price = models.FloatField(max_length=10, null=True, blank=True, default=0.00)

    # Carton size
    carton_size = models.IntegerField(null=False, blank=False)

    product_barcode = models.IntegerField(null=False, blank=False, default=0)
    carton_barcode = models.IntegerField(null=False, blank=False, default=0)

    is_active = models.BooleanField(default=True)

    gst = models.FloatField(max_length=5, default=0.00)
    factory_gst = models.FloatField(max_length=10, default=0.00)
    factory_sale = models.FloatField(max_length=10, default=0.00)

    distributor_margin_rate = models.FloatField(max_length=5, default=0.00, )
    distributor_margin_price = models.FloatField(max_length=10, default=0.00)
    distributor_gst = models.FloatField(max_length=10, default=0.00)
    distributor_sale = models.FloatField(max_length=10, default=0.00)

    retailer_margin_rate = models.FloatField(max_length=5, default=0.00, )
    retailer_margin_price = models.FloatField(max_length=10, default=0.00)
    retailer_gst = models.FloatField(max_length=10, default=0.00)
    retailer_sale = models.FloatField(max_length=10, default=0.00)

    retailer_base_price = models.FloatField(max_length=10, default=0.00)
    retailer_base_gst = models.FloatField(max_length=10, default=0.00)
    mrp = models.FloatField(max_length=10, default=0.00)
    # new
    product_discount=models.FloatField(max_length=5, default=0.00)

    # ==================================================
    @property
    def distributorBasePrice(self):
        try:
            price= round(self.distributor_sale - self.distributor_gst,2)
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)
    
    @property
    def ProductDiscountAmount(self):
        
        """
        done
        """
        try:
            base_price= (self.distributor_sale - self.distributor_gst)
            price= (base_price*self.product_discount*self.carton_size)/100
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)
    
    def ProductDiscountAmountUse(self):
        
        """
        done
        """
        try:
            base_price= (self.distributor_sale - self.distributor_gst)
            price= (base_price*self.product_discount*self.carton_size)/100
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)
    
    def SubTotalAmount(self):
        
        """
        done
        """
        try:
            carton_base_price= (self.distributor_sale - self.distributor_gst)*self.carton_size
            price= carton_base_price-self.ProductDiscountAmountUse()
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)


    @property
    def distributorCartonGstPrice(self):
        """done"""
        try:
            product_discout_price= ((self.distributor_sale - self.distributor_gst)*self.product_discount*self.carton_size)/100
            price=(product_discout_price*self.gst)/100
        except:
            price=0
        return round(price,2)
    def distributorCartonGstPriceUse(self):
        """done"""
        try:
            product_discout_price= ((self.distributor_sale - self.distributor_gst)*self.product_discount*self.carton_size)/100
            price=(product_discout_price*self.gst)/100
        except:
            price=0
        return round(price,2)
    
    @property
    def ProductMainAmount(self):
        """
        done
        """
        try:
            product_discout_price= ((self.distributor_sale - self.distributor_gst)*self.product_discount*self.carton_size)/100
            price=product_discout_price+(product_discout_price*self.gst)/100
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)

    def ProductMainAmountUse(self):
        """
        done
        """
        try:
            product_discout_price= ((self.distributor_sale - self.distributor_gst)*self.product_discount*self.carton_size)/100
            price=product_discout_price+(product_discout_price*self.gst)/100
                
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)

    @property
    def distributorCartonBasePrice(self):
        """
        done
        """
        try:
            price= (self.distributor_sale - self.distributor_gst)*self.carton_size
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)
    
    @property
    def distributorCartonSalePrice(self):
        try:
            price= (self.distributor_sale*self.carton_size)
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)
    
    @property
    def distributorCartonGstPrice(self):
        try:
            base_price= self.distributor_sale - self.distributor_gst
            price= (base_price*self.carton_size*self.gst/100)
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)




    def __str__(self):
        return self.product_name
    #
    def save(self, *args, **kwargs):
        if not self.image:
            default_image_path = os.path.join(settings.STATIC_ROOT, 'static', 'default_product.png')
            if os.path.exists(default_image_path):
                with open(default_image_path, 'rb') as f:
                    self.image.save('default_product.png', File(f), save=False)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    product_images = models.ImageField(upload_to='product_images/', blank=False, null=False)

    def __str__(self):
        return self.product.product_name


class ProductSize(models.Model):
    size_name = models.CharField(max_length=100, blank=False, null=False)
    size_volume = models.CharField(max_length=50, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_sizes')

    def __str__(self):
        return self.size_name


class ProductFlavour(models.Model):
    flavour_name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_flavours')

    def __str__(self):
        return self.flavour_name


class ProductSpecification(models.Model):
    specification_name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_specifications')

    def __str__(self):
        return self.specification_name


# ==================

