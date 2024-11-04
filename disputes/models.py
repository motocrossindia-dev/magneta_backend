from django.db import models

from accounts.models import UserBase
from distributors.models import RetailerOrders
from orders.models import Order


class Dispute(models.Model):

    factory_order = models.ForeignKey(Order, on_delete=models.PROTECT, blank=True, null=True)
    Distributor_order = models.ForeignKey(RetailerOrders, on_delete=models.PROTECT, blank=True, null=True)

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    # Retailor_order = models.ForeignKey('orders.Order', on_delete=models.PROTECT,blank=True, null=True)

    created_by = models.ForeignKey(UserBase, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
