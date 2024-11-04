from django.db import models
from django.utils import timezone

from accounts.models import UserBase
from distributors.models import RetailerMainOrders


class distributor_sales(models.Model):
    sales_person = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='sales_sales_person')
    distributor = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='sales_distributor')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'distributor_sales'
        unique_together = ('sales_person', 'distributor')

    def __str__(self):
        return str(f"{self.distributor}-{self.sales_person}")


class salesPerson_orders(models.Model):
    sales_person = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='sales_person_orders')
    order = models.ForeignKey(RetailerMainOrders, on_delete=models.CASCADE, related_name='retailer_main_orders')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sales_person', 'order')

    def __str__(self):
        return f"{self.sales_person}"


# partial payments
class salesRetailerTransactions(models.Model):
    sales_person = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='sales_person_transaction')
    distributor = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='sales_distributor_transaction')
    retailer = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='sales_retailer_transaction')
    transaction_amount = models.FloatField(max_length=10)
    mode_of_payment = models.CharField(max_length=20, default="Cash")
    details = models.CharField(max_length=255, null=True, blank=True)

    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(f"{self.distributor}-{self.sales_person}")




class salesPersonordersTransaction(models.Model):
    sales_person = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='sales_person_orders_transaction')
    salesRetailerTransactions = models.ForeignKey(salesRetailerTransactions, on_delete=models.CASCADE,
                                                  related_name='sales_person_retailer_transaction')
    order = models.ForeignKey(RetailerMainOrders, on_delete=models.CASCADE,
                              related_name='retailer_main_orders_transaction')
    amount_settled = models.FloatField(max_length=10)
    pending_amount = models.FloatField(max_length=10)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sales_person', 'order')

    def __str__(self):
        return f"{self.sales_person}"


class retailerTransactionDetails(models.Model):
    retailer = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='retailer_retailerTransactionDetails')
    amount = models.FloatField(max_length=10)
    totalSaleAmount = models.FloatField(max_length=10, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'retailer Sale Details'

    def __str__(self):
        return f"{self.retailer}"


# ========================================================================================
# ============================= Cash in Hand of Sales Person =============================
# ========================================================================================

class salesPersonCashInHand(models.Model):
    sales_person = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='sales_person_cash_in_hand')
    cash_in_hand = models.FloatField(max_length=10, default=0.0)
    amount_transferred_to_distributer = models.FloatField(max_length=10, default=0.0)
    total = models.FloatField(max_length=10, default=0.0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"{self.sales_person}")


class transactionFromSalesToDistributor(models.Model):
    sales_person = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='transactionSales')
    distributor = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='transactionDistributor')
    amount = models.FloatField(max_length=10, default=0.0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f"{self.sales_person}")


class ProductDiscount(models.Model):
    max_product_discount=models.FloatField(max_length=50)
    max_invoice_discount=models.FloatField(max_length=50)

    def __str__(self):
        return f"{self.max_product_discount}-{self.max_invoice_discount}"