from django.db import models

from accounts.models import UserBase
from products.models import Product


class MainOrders(models.Model):
    status_choices = (
        ('Requested', 'Requested'),
        ('Accepted', 'Accepted'),
        ('Verifying Payment', 'Verifying Payment'),
        ('Amount Paid', 'Amount Paid'),
        ('In Process', 'In Process'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    distributor = models.ForeignKey(UserBase, on_delete=models.PROTECT, related_name='Distributer')
    order_date = models.DateField()
    status = models.CharField(max_length=30, choices=status_choices, default="Requested")
    mode_of_payment = models.CharField(max_length=15, default="Cash")
    payment_status = models.CharField(max_length=20, default="Unpaid")
    order_by_factory = models.BooleanField(default=False)
    CGST = models.FloatField(max_length=5, default=0.00)
    SGST = models.FloatField(max_length=5, default=0.00)
    IGST = models.FloatField(max_length=5, default=0.00)
    gst = models.FloatField(max_length=5, default=0.00)
    sub_total = models.FloatField(max_length=10, default=0.00)
    grand_total = models.FloatField(max_length=10, default=0.00)

    order_number = models.CharField(max_length=11, editable=False, default='00000000000')

    CGST_rate = models.FloatField(max_length=5, default=0.00)
    SGST_rate = models.FloatField(max_length=5, default=0.00)
    IGST_rate = models.FloatField(max_length=5, default=0.00)
    gst_rate = models.FloatField(max_length=5, default=0.00)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Round the grand_total attribute to two decimal places
        self.grand_total = round(self.grand_total, 2)
        # Call the superclass's save() method to perform the actual saving
        super(MainOrders, self).save(*args, **kwargs)

    def __str__(self):
        # return f"{self.distributor}_{self.distributor.id}"
        return str(self.id)


# Create your models here.
class Order(models.Model):
    main_order = models.ForeignKey(MainOrders, on_delete=models.PROTECT, related_name='Main_order', default=1)
    product_name = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='Product_name', default=4)
    requested_quantity = models.IntegerField(default=0)
    accepted_quantity = models.IntegerField(default=0)

    factory_base_price = models.FloatField(max_length=10, default=0.00)
    factory_gst_price = models.FloatField(max_length=10, default=0.00)
    factory_sale = models.FloatField(max_length=10, default=0.00)

    carton_size = models.IntegerField(default=0)
    price_per_carton = models.FloatField(max_length=10, default=0.00)

    mrp = models.FloatField(max_length=6, default=0.00)

    discount = models.FloatField(max_length=5, default=0.00)
    discount_amount = models.FloatField(max_length=10, default=0.00)

    sum = models.FloatField(max_length=10, default=0.00)

    CGST = models.FloatField(max_length=5, default=0.00)
    SGST = models.FloatField(max_length=5, default=0.00)
    IGST = models.FloatField(max_length=5, default=0.00)
    gst = models.FloatField(max_length=5, default=0.00)
    amount = models.FloatField(default=0.00)


class PaymentTrack(models.Model):
    status_choices = (
        ('Requested', 'Requested'),
        ('Accepted', 'Accepted'),
        ('Verifying Payment', 'Verifying Payment'),
        ('Amount Paid', 'Amount Paid'),
        ('In Process', 'In Process'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    main_order = models.ForeignKey(MainOrders, on_delete=models.PROTECT, related_name='Main_Order', default=1)
    status = models.CharField(max_length=30, choices=status_choices)
    utrNo = models.CharField(max_length=40, default="0", blank=True, null=True)
    cash = models.FloatField(max_length=10, default=0.00, blank=True, null=True)
    cheque = models.IntegerField(default=0, blank=True, null=True)
    credit = models.FloatField(max_length=10, default=0.00, blank=True, null=True)
    updated_by = models.CharField(max_length=30)
    updator_contact = models.CharField(max_length=15)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.updated_by


class GST(models.Model):
    gst = models.FloatField(max_length=5, default=0.00)
    cgst = models.FloatField(max_length=5, default=0.00)
    sgst = models.FloatField(max_length=5, default=0.00)
    igst = models.FloatField(max_length=5, default=0.00)


class FactoryToCustomer(models.Model):
    order_number = models.CharField(max_length=11, editable=False)
    sold_by = models.ForeignKey(UserBase, on_delete=models.PROTECT, related_name='sold_by')
    product_name = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='Product_sold', default=4)
    order_date = models.DateField()
    mode_of_payment = models.CharField(max_length=15, default="Cash")
    payment_status = models.CharField(max_length=20, default="Unpaid")
    quantity = models.IntegerField(default=0)
    mrp = models.FloatField(max_length=6, default=0.00)
    amount = models.FloatField(default=0.00)

    def __str__(self):
        return str(self.id)


