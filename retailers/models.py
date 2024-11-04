from django.db import models

from accounts.models import UserBase
from products.models import Product


# Create your models here.


class CustomerMainOrders(models.Model):
    retailer = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    orderDate = models.DateField()
    modeOfPayment = models.CharField(max_length=15, default="Cash")
    customerFullName = models.CharField(max_length=50, default='Default Customer', blank=True)
    customerPhoneNumber = models.CharField(max_length=10, default='0000000000', blank=True)
    grandTotal = models.FloatField(max_length=10, default=0.00)

    orderNumber = models.CharField(max_length=15, editable=False, default='00000000000')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class CustomerOrders(models.Model):
    customerMainOrder = models.ForeignKey(CustomerMainOrders, on_delete=models.PROTECT)
    productId = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='customer_products')
    productName = models.CharField(max_length=100, default="Mango")

    quantity = models.IntegerField()

    mrp = models.FloatField(max_length=6, default=0.00)

    sum = models.FloatField(max_length=10, default=0.00)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
