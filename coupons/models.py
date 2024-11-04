from django.contrib.auth.models import User
from django.db import models


# Coupon Table
class Coupon(models.Model):
    generatedBy = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    category_color = models.CharField(max_length=10, default='#000000')
    coupon_name = models.CharField(max_length=100)

    applicable_discount = models.FloatField()
    is_type_flat = models.BooleanField(default=False)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # applicable_to_all = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.coupon_name
