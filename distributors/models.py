
from django.db import models

from accounts.models import UserBase
from products.models import Product


class RetailerMainOrders(models.Model):
    distributor = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='Distributer_retailer')
    retailer = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    order_date = models.DateField()
    mode_of_payment = models.CharField(max_length=15, default="Cash")
    payment_status = models.CharField(max_length=20, default="Unpaid")
    order_by_factory = models.BooleanField(default=False)
    CGST = models.FloatField(max_length=5, default=0.00)
    SGST = models.FloatField(max_length=5, default=0.00)
    IGST = models.FloatField(max_length=5, default=0.00)
    gst = models.FloatField(max_length=5, default=0.00)
    sub_total = models.FloatField(max_length=10, default=0.00)
    grand_total = models.FloatField(max_length=10, default=0.00)
    pending_amount = models.FloatField(max_length=10, default=0.00)

    order_number = models.CharField(max_length=11, editable=False, default='00000000000')

    CGST_rate = models.FloatField(max_length=5, default=0.00)
    SGST_rate = models.FloatField(max_length=5, default=0.00)
    IGST_rate = models.FloatField(max_length=5, default=0.00)
    gst_rate = models.FloatField(max_length=5, default=0.00)
    # new
    discount_percentage = models.FloatField(default=0.00)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        # return f"{self.distributor}_{self.distributor.id}"
        return str(self.id)

    def save(self, *args, **kwargs):
        """Set pending_amount to 0 if payment_status is 'paid'."""
        if self.payment_status.lower() == "paid":
            self.pending_amount = 0.00
        super().save(*args, **kwargs)


    # new==
    def total_pending_amount_by_retailer(self, retailer_id):
        """Calculate total pending amount for a specific retailer, avoiding duplicates."""
        orders = RetailerMainOrders.objects.filter(
            distributor=self.distributor,
            retailer_id=retailer_id
        ).distinct()
        total_pending = 0.0

        for order in orders:
            # Exclude orders with mode_of_payment that don't contribute to pending amount
            if order.mode_of_payment.lower() not in ["free sample",
                                                     "paid"] and order.payment_status.lower() != "cancelled":
                total_pending += order.pending_amount

        return total_pending

    def total_cancelled_amount_by_retailer(self, retailer_id):
        """Calculate total cancelled amount based on pending amounts for a specific retailer."""
        orders = RetailerMainOrders.objects.filter(
            distributor=self.distributor,
            retailer_id=retailer_id,
            payment_status="cancelled"
        ).distinct()

        total_cancelled = sum(order.pending_amount for order in orders)
        return total_cancelled

    # def total_cancelled_amount_by_retailer(self, retailer_id):
    #     """Calculate total cancelled amount for a specific retailer, avoiding duplicates."""
    #     orders = RetailerMainOrders.objects.filter(
    #         distributor=self.distributor,
    #         retailer_id=retailer_id,
    #         payment_status__contains="cancelled"
    #     ).distinct()
    #     total_cancelled = sum(order.grand_total for order in orders)
    #
    #     return total_cancelled

    def total_bill_amount_by_retailer(self, retailer_id):
        """Calculate total bill amount based on pending amounts for a specific retailer, excluding cancelled orders."""
        orders = RetailerMainOrders.objects.filter(
            distributor=self.distributor,
            retailer_id=retailer_id
        ).exclude(
            payment_status="cancelled"
        ).distinct()

        total_bill = sum(order.pending_amount for order in orders)
        return total_bill

    # def total_bill_amount_by_retailer(self, retailer_id):
    #     """Calculate total bill amount for a specific retailer, avoiding duplicates."""
    #     orders = RetailerMainOrders.objects.filter(
    #         distributor=self.distributor,
    #         retailer_id=retailer_id
    #     ).distinct()
    #
    #     total_bill = sum(order.grand_total for order in orders if order.payment_status.lower() != "cancelled")
    #
    #
    #     return total_bill

    # new==

    # def total_pending_amount_by_retailer(self, retailer_id):
    #     """Calculate total pending amount for a specific retailer, avoiding duplicates."""
    #     orders = RetailerMainOrders.objects.filter(distributor=self.distributor,retailer_id=retailer_id).distinct()
    #     total_pending = 0.0
    #
    #     for order in orders:
    #         if order.mode_of_payment.lower() in ["free sample", "paid","cancelled"] or order.payment_status.lower() == "cancelled":
    #             total_pending -= order.pending_amount
    #         else:
    #             total_pending += order.pending_amount
    #
    #         # print(f"Order ID: {order.id}, Pending Amount: {order.pending_amount}, Total Pending: {total_pending}")
    #
    #     return total_pending
    #
    # def total_cancelled_amount_by_retailer(self, retailer_id):
    #     """Calculate total cancelled amount for a specific retailer, avoiding duplicates."""
    #     orders = RetailerMainOrders.objects.filter(distributor=self.distributor,retailer_id=retailer_id,
    #                                                payment_status__iexact="cancelled").distinct()
    #     total_cancelled = 0.0
    #
    #     for order in orders:
    #         total_cancelled += order.grand_total
    #
    #         # print(f"Cancelled Order ID: {order.id}, Pending Amount: {order.grand_total}, Total Cancelled: {total_cancelled}")
    #
    #     return total_cancelled
    #
    # def total_bill_amount_by_retailer(self, retailer_id):
    #     """Calculate total bill amount for a specific retailer, avoiding duplicates."""
    #     orders = RetailerMainOrders.objects.filter(distributor=self.distributor,retailer_id=retailer_id).distinct()
    #     total_bill = 0.0
    #
    #     for order in orders:
    #         if order.payment_status.lower() == "cancelled":
    #             total_bill -= order.grand_total
    #         else:
    #             total_bill += order.grand_total
    #
    #         # print(f"Order ID: {order.id}, Pending Amount: {order.grand_total}, Total Bill: {total_bill}")
    #
    #     return total_bill

    # def total_pending_amount_by_retailer(self, retailer_id):
    #     """Calculate total pending amount for a specific retailer, deducting amounts based on conditions."""
    #     # Get all orders for the specific retailer
    #     orders = RetailerMainOrders.objects.filter(retailer_id=retailer_id)
    #
    #     total_pending = 0.0
    #     for order in orders:
    #         if order.mode_of_payment.lower() in ["free sample", "paid"] or order.payment_status.lower() == "cancelled":
    #             total_pending -= order.pending_amount  # Deduct if the conditions are met
    #         else:
    #             total_pending += order.pending_amount  # Add if the conditions are not met
    #
    #     return total_pending
    #
    #
    # def total_cancelled_amount_by_retailer(self, retailer_id):
    #     """Calculate total cancelled amount for a specific retailer."""
    #     orders = RetailerMainOrders.objects.filter(retailer_id=retailer_id, payment_status__iexact="cancelled")
    #
    #     total_cancelled = 0.0
    #     for order in orders:
    #         total_cancelled += order.pending_amount  # Add all cancelled order pending amounts
    #
    #     return total_cancelled
    #
    # def total_bill_amount_by_retailer(self, retailer_id):
    #     """Calculate total pending amount for a specific retailer, deducting amounts only for cancelled orders."""
    #     # Get all orders for the specific retailer
    #     orders = RetailerMainOrders.objects.filter(retailer_id=retailer_id)
    #
    #     total_pending = 0.0
    #     for order in orders:
    #         if order.payment_status.lower() == "cancelled":
    #             total_pending -= order.pending_amount  # Deduct if the order is cancelled
    #         else:
    #             total_pending += order.pending_amount  # Add if the order is not cancelled
    #
    #     return total_pending


    # ===========================
    @property
    def retailer_orders_discounts_total(self):
        total_discount = 0.0
        retailer_orders = self.retailer_orders1.all()  # Access all related RetailerOrders
        for order in retailer_orders:
            total_discount += order.product_discount  # Sum up each order's discount
        return total_discount

    @property
    def orders_sum(self):
        try:
            order_sum=sum(order.discounted_amount() for order in self.retailer_orders1.all())
        except:
            order_sum=0.0
        return round(order_sum,2)

    @property
    def GrandTotalAmount(self):
        try:
            # Subtotal calculation
            sub_total = sum(order.product_id.SubTotalAmount() for order in self.retailer_orders1.all())
            
            # Discounted invoice amount calculation
            invoice_discount = sub_total * (self.discount_percentage / 100)
            invoice_price = sub_total - invoice_discount
            
            # SGST calculation
            sgst_total = (sub_total - invoice_discount) * (self.SGST_rate / 100) if self.SGST_rate else 0.0
            
            # CGST calculation
            cgst_total = (sub_total - invoice_discount) * (self.CGST_rate / 100) if self.CGST_rate else 0.0
            
            # IGST calculation
            igst_total = (sub_total - invoice_discount) * (self.IGST_rate / 100) if self.IGST_rate else 0.0
            
            # Grand total price calculation
            price = (sub_total + sgst_total + cgst_total + igst_total) - invoice_discount
            
            # Debug prints
            print(type(sub_total), '=========sub')
            print(type(sgst_total), '====sgst')
            print(type(cgst_total), '=====cgst')
            print(type(igst_total), '=========igst')
            print(type(invoice_discount), '==========invoice discount')
            print(type(price), '==========grand total')
        
        except Exception as e:
            print(e, '=========price gd')
            price = 0.0  # Default price in case of error
        
        return round(price, 2)  # Return rounded grand total amount
        

    
    def invoice_discounted_amount(self):
        "done"
        try:
            order_sum=sum(order.product_id.SubTotalAmount() for order in self.retailer_orders1.all())*(self.discount_percentage/100)
        except:
            order_sum=0.0
        return round(order_sum,2)
    
    def sub_total_amount(self):
        "done"
        try:
            order_sum=sum(order.product_id.SubTotalAmount() for order in self.retailer_orders1.all())
        except:
            order_sum=0.0
        return round(order_sum,2)

    def sgst_amount(self):
        price=(self.sub_total_amount-self.invoice_discounted_amount)*self.SGST_rate/100 or 0.0
        return round(price,2)

    def cgst_amount(self):
        price=(self.sub_total_amount-self.invoice_discounted_amount)*self.CGST_rate/100 or 0.0
        return round(price,2)

    def igst_amount(self):
        price=(self.sub_total_amount-self.invoice_discounted_amount)*self.IGST_rate/100 or 0.0
        return round(price,2)

    
    @property
    def invoice_discounted_amount(self):
        "done"
        try:
            order_sum=sum(order.product_id.SubTotalAmount() for order in self.retailer_orders1.all())*(self.discount_percentage/100)
        except:
            order_sum=0.0
        return round(order_sum,2)

    @property
    def sub_total_amount(self):
        "done"
        try:
            order_sum=sum(order.product_id.SubTotalAmount() for order in self.retailer_orders1.all())
        except:
            order_sum=0.0
        return round(order_sum,2)
    @property
    def orders_discount_sum(self):
        "done"


        try:
 
            order_sum=sum(order.product_id.ProductDiscountAmountUse() for order in self.retailer_orders1.all())
        except Exception as e:
            print(e)
            order_sum=0.0
        return round(order_sum,2)
    @property
    def orders_gst_sum(self):
        "done"
        try:
            order_sum=sum(order.product_id.distributorCartonGstPriceUse() for order in self.retailer_orders1.all())
        except:
            order_sum=0.0
        return round(order_sum,2)
    @property
    def orders_product_main_sum(self):
        "done"
        try:
            order_sum=sum(order.product_id.ProductMainAmountUse() for order in self.retailer_orders1.all())
        except:
            order_sum=0.0
        return round(order_sum,2)




class RetailerOrders(models.Model):
    retailer_main_order = models.ForeignKey(RetailerMainOrders, on_delete=models.PROTECT,
                                            related_name='retailer_orders1')
    product_id = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=100, default="Mango")

    quantity = models.IntegerField()

    distributor_margin_rate = models.FloatField(max_length=5, default=0.00, )
    distributor_margin_price = models.FloatField(max_length=10, default=0.00)
    distributor_gst = models.FloatField(max_length=10, default=0.00)
    distributor_sale = models.FloatField(max_length=10, default=0.00)

    carton_size = models.IntegerField()
    price_per_carton = models.FloatField()

    mrp = models.FloatField(max_length=6, default=0.00)

    sum = models.FloatField(max_length=10, default=0.00)
    CGST = models.FloatField(max_length=5, default=0.00)
    SGST = models.FloatField(max_length=5, default=0.00)
    IGST = models.FloatField(max_length=5, default=0.00)
    gst = models.FloatField(max_length=5, default=0.00)
    amount = models.FloatField(default=0.00)

    # pending_amount = models.FloatField(default=0.00)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        # return f"{self.distributor}_{self.distributor.id}"
        return str(self.id)
    


    # =========================================================


    @property
    def ProductDiscountAmount(self):

        """
        done
        """
        try:
            base_price= (self.product_id.distributor_sale - self.product_id.distributor_gst)
            price= (base_price*self.product_id.product_discount*self.product_id.carton_size)/100

        except (TypeError, AttributeError):
            price= 0
        return round(price,2)

    def ProductDiscountAmountUse(self):

        """
        done
        """
        try:
            base_price= (self.product_id.distributor_sale - self.product_id.distributor_gst)
            price= (base_price*self.product_id.product_discount*self.product_id.carton_size)/100
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)

    def SubTotalAmount(self):

        """
        done
        """
        try:
            carton_base_price= (self.product_id.distributor_sale - self.product_id.distributor_gst)*self.product_id.carton_size
            price= carton_base_price-self.product_id.ProductDiscountAmountUse()
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)


    @property
    def distributorCartonGstPrice(self):
        """done"""
        try:
            product_discout_price= ((self.product_id.distributor_sale - self.product_id.distributor_gst)*self.product_id.product_discount*self.product_id.carton_size)/100
            price=(product_discout_price*self.product_id.gst)/100
        except:
            price=0
        return round(price,2)

    def distributorCartonGstPriceUse(self):
        """done"""
        try:
            product_discout_price= ((self.product_id.distributor_sale - self.product_id.distributor_gst)*self.product_id.product_discount*self.product_id.carton_size)/100
            price=(product_discout_price*self.product_id.gst)/100
        except:
            price=0
        return round(price,2)

    @property
    def ProductMainAmount(self):
        """
        done
        """
        try:
            product_discout_price= ((self.product_id.distributor_sale - self.product_id.distributor_gst)*self.product_id.product_discount*self.product_id.carton_size)/100
            price=product_discout_price+(product_discout_price*self.product_id.gst)/100

        except (TypeError, AttributeError):
            price= 0
        return round(price,2)
    def ProductMainAmountUse(self):
        """
        done
        """
        try:
            product_discout_price= ((self.product_id.distributor_sale - self.product_id.distributor_gst)*self.product_id.product_discount*self.product_id.carton_size)/100
            price=product_discout_price+(product_discout_price*self.product_id.gst)/100

        except (TypeError, AttributeError):
            price= 0
        return round(price,2)

    @property
    def distributorCartonBasePrice(self):
        """
        done
        """
        try:
            price= round((self.product_id.distributor_sale - self.product_id.distributor_gst)*self.product_id.carton_size,2)
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)

    @property
    def distributorCartonSalePrice(self):
        try:
            price= (self.product_id.distributor_sale*self.product_id.carton_size)
        except (TypeError, AttributeError):
            price= 0
        return round(price,2)


    # =========================================================
    



    def discounted_amount(self):
        discount_amount = (self.carton_size * self.distributor_sale * self.product_id.product_discount) / 100
        discounted_amount=self.amount - (discount_amount*self.quantity)
        return discounted_amount


    @property
    def gst_after_discount(self):
        try:
            carton_price = self.carton_size * self.distributor_sale
            discounted_gst=carton_price*self.quantity-(self.product_id.product_discount/ 100)*self.gst
        except:
            discounted_gst=0.0
        return discounted_gst


    @property
    def product_discount(self):
        """
        price per unit
        """
        carton_price = self.carton_size * self.distributor_sale
        discount_amount = carton_price * self.product_id.product_discount/ 100
        try:
            discount=discount_amount*self.quantity
        except:
            discount=0


        return discount
    @property
    def price_per_product(self):
        """
        price per unit
        """
        print("=====product per====here discount",self.product_id.product_discount)
        carton_price = self.carton_size * self.distributor_sale
        discount_amount = carton_price * self.product_id.product_discount/10

        return discount_amount


class DistributorStock(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.PROTECT)
    distributor_id = models.ForeignKey(UserBase, on_delete=models.PROTECT, related_name='DistributerStock')
    quantity = models.IntegerField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.product_id) + '_' + str(self.distributor_id) + '_' + str(self.quantity)


"""
def calculate_tax():
    distributor_base_price = distributor_sale - distributor_gst
    # a=10-2
    carton_distributor_base_price=distributor_base_price*carton_size
    # b=a*5
    # b=40
    discount=carton_distributor_base_price*product_discount/100
    # c=b*50/100
    # c=20
    
    discounted_price=(carton_distributor_base_price-discount)*product_quntity
    # d=b-c=>(40-20)2=40
    
    gst_price=discounted_price*gst/100
    # e=d*20/100
    # e=40*20/100==>8
    product_amount=discounted_price+gst_price
    # f=d+e==>40+8==48
    
    total_product_amount=sum(product_amount)
    total_gst_amount=sum(gst_price)
    
    sub_total=sum(discounted_price)
    invoice_discounted_amount=sub_total-(sub_total*invoice_discount)# invoice_discount input
    
    sgst=invoice_discounted_amount*sgst_percent/100
    cgst=invoice_discounted_amount*cgst_percent/100
    igst=invoice_discounted_amount*igst_percent/100
    
    grand_total=invoice_discounted_amount+sgst+cgst+igst

"""
#
# class DistributorTransaction(models.Model):
#     distributor_id = models.ForeignKey(UserBase, on_delete=models.PROTECT, related_name='DistributerTransaction')
#     sales_person = models.ForeignKey(UserBase, on_delete=models.PROTECT, related_name='sales_transaction')
#
#
#     quantity = models.IntegerField()
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return str(self.distributor_id)
# ======================


# from decimal import Decimal
# from django.db.models import Sum, F
#
#
# def calculate_product_tax(order_item):
#     distributor_base_price = order_item.distributor_sale - order_item.distributor_gst
#     carton_base_price = distributor_base_price * order_item.carton_size
#     discount = carton_base_price * (order_item.product_id.product_discount / Decimal('100'))
#     discounted_price = (carton_base_price - discount) * order_item.quantity
#     gst_price = discounted_price * (order_item.gst / Decimal('100'))
#     product_amount = discounted_price + gst_price
#
#     # Update the order item with calculated values
#     order_item.distributor_margin_price = order_item.distributor_sale - distributor_base_price
#     order_item.sum = discounted_price
#     order_item.CGST = gst_price / 2
#     order_item.SGST = gst_price / 2
#     order_item.IGST = Decimal('0')
#     order_item.amount = product_amount
#     order_item.save()
#
#     return {
#         'name': order_item.product_name,
#         'distributor_base_price': distributor_base_price,
#         'carton_base_price': carton_base_price,
#         'discount': discount,
#         'discounted_price': discounted_price,
#         'gst_price': gst_price,
#         'product_amount': product_amount
#     }
#
#
# def calculate_invoice_totals(main_order):
#     order_items = main_order.retailer_orders1.all()
#
#     # Calculate totals
#     totals = order_items.aggregate(
#         total_discounted_price=Sum('sum'),
#         total_gst_amount=Sum('CGST') + Sum('SGST') + Sum('IGST'),
#         total_product_amount=Sum('amount')
#     )
#
#     invoice_discounted_amount = totals['total_discounted_price'] * (
#                 Decimal('100') - main_order.discount_percentage) / Decimal('100')
#
#     sgst = invoice_discounted_amount * (main_order.SGST_rate / Decimal('100'))
#     cgst = invoice_discounted_amount * (main_order.CGST_rate / Decimal('100'))
#     igst = invoice_discounted_amount * (main_order.IGST_rate / Decimal('100'))
#
#     grand_total = invoice_discounted_amount + sgst + cgst + igst
#
#     # Update main order with calculated values
#     main_order.sub_total = totals['total_product_amount']
#     main_order.CGST = cgst
#     main_order.SGST = sgst
#     main_order.IGST = igst
#     main_order.gst = totals['total_gst_amount']
#     main_order.grand_total = grand_total
#     main_order.pending_amount = grand_total
#     main_order.save()
#
#     return {
#         'total_discounted_price': totals['total_discounted_price'],
#         'total_gst_amount': totals['total_gst_amount'],
#         'total_product_amount': totals['total_product_amount'],
#         'invoice_discounted_amount': invoice_discounted_amount,
#         'sgst': sgst,
#         'cgst': cgst,
#         'igst': igst,
#         'grand_total': grand_total
#     }
#
#
# def generate_invoice(main_order):
#     order_items = main_order.retailer_orders1.all()
#
#     products = [calculate_product_tax(item) for item in order_items]
#     totals = calculate_invoice_totals(main_order)
#
#     return {
#         'products': products,
#         'totals': totals
#     }

# from typing import List, Dict
# from decimal import Decimal
#
# """
# # General Invoice Calculation Example
#
# Let's consider an invoice with two items: Item A and Item B.
#
# ## Given Information:
# - Invoice Discount: 10%
# - SGST: 9%
# - CGST: 9%
# - IGST: 0%
#
# ### Item A:
# - Distributor Sale Price: 100
# - Distributor GST: 18
# - Carton Size: 10
# - Product Discount: 50%
# - Product Quantity: 2
# - GST: 18%
#
# ### Item B:
# - Distributor Sale Price: 200
# - Distributor GST: 36
# - Carton Size: 5
# - Product Discount: 40%
# - Product Quantity: 3
# - GST: 18%
#
# ## Calculations:
#
# ### 1. Item A Calculations:
# a) Distributor Base Price = Distributor Sale Price - Distributor GST
#    = 100 - 18 = 82
#
# b) Carton Base Price = Distributor Base Price * Carton Size
#    = 82 * 10 = 820
#
# c) Discount = Carton Base Price * Product Discount
#    = 820 * 50% = 410
#
# d) Discounted Price = (Carton Base Price - Discount) * Product Quantity
#    = (820 - 410) * 2 = 820
#
# e) GST Price = Discounted Price * GST
#    = 820 * 18% = 147.60
#
# f) Product Amount = Discounted Price + GST Price
#    = 820 + 147.60 = 967.60
#
# ### 2. Item B Calculations:
# a) Distributor Base Price = 200 - 36 = 164
#
# b) Carton Base Price = 164 * 5 = 820
#
# c) Discount = 820 * 40% = 328
#
# d) Discounted Price = (820 - 328) * 3 = 1,476
#
# e) GST Price = 1,476 * 18% = 265.68
#
# f) Product Amount = 1,476 + 265.68 = 1,741.68
#
# ### 3. Invoice Totals:
# a) Total Discounted Price = 820 + 1,476 = 2,296
#
# b) Total GST Amount = 147.60 + 265.68 = 413.28
#
# c) Total Product Amount = 967.60 + 1,741.68 = 2,709.28
#
# d) Invoice Discounted Amount = Total Discounted Price * (100% - Invoice Discount)
#    = 2,296 * 90% = 2,066.40
#
# e) SGST = Invoice Discounted Amount * SGST Rate
#    = 2,066.40 * 9% = 185.98
#
# f) CGST = Invoice Discounted Amount * CGST Rate
#    = 2,066.40 * 9% = 185.98
#
# g) IGST = Invoice Discounted Amount * IGST Rate
#    = 2,066.40 * 0% = 0
#
# h) Grand Total = Invoice Discounted Amount + SGST + CGST + IGST
#    = 2,066.40 + 185.98 + 185.98 + 0 = 2,438.36
#
# ## Summary:
# - Item A Total: 967.60
# - Item B Total: 1,741.68
# - Invoice Subtotal: 2,709.28
# - Invoice Discount: 229.60
# - SGST: 185.98
# - CGST: 185.98
# - IGST: 0
# - Grand Total: 2,438.36
# """
# def calculate_product_tax(item: Dict[str, Decimal]) -> Dict[str, Decimal]:
#
#     distributor_base_price = item['distributor_sale'] - item['distributor_gst']
#     carton_base_price = distributor_base_price * item['carton_size']
#     discount = carton_base_price * item['product_discount'] / Decimal('100')
#     discounted_price = (carton_base_price - discount) * item['product_quantity']
#     gst_price = discounted_price * item['gst'] / Decimal('100')
#     product_amount = discounted_price + gst_price
#
#     return {
#         'name': item['name'],
#         'distributor_base_price': distributor_base_price,
#         'carton_base_price': carton_base_price,
#         'discount': discount,
#         'discounted_price': discounted_price,
#         'gst_price': gst_price,
#         'product_amount': product_amount
#     }
#
#
# def calculate_invoice_totals(products: List[Dict[str, Decimal]], invoice_discount: Decimal,
#                              sgst_percent: Decimal, cgst_percent: Decimal, igst_percent: Decimal) -> Dict[str, Decimal]:
#     total_discounted_price = sum(p['discounted_price'] for p in products)
#     total_gst_amount = sum(p['gst_price'] for p in products)
#     total_product_amount = sum(p['product_amount'] for p in products)
#
#     invoice_discounted_amount = total_discounted_price * (Decimal('100') - invoice_discount) / Decimal('100')
#
#     sgst = invoice_discounted_amount * sgst_percent / Decimal('100')
#     cgst = invoice_discounted_amount * cgst_percent / Decimal('100')
#     igst = invoice_discounted_amount * igst_percent / Decimal('100')
#
#     grand_total = invoice_discounted_amount + sgst + cgst + igst
#
#     return {
#         'total_discounted_price': total_discounted_price,
#         'total_gst_amount': total_gst_amount,
#         'total_product_amount': total_product_amount,
#         'invoice_discounted_amount': invoice_discounted_amount,
#         'sgst': sgst,
#         'cgst': cgst,
#         'igst': igst,
#         'grand_total': grand_total
#     }
#
#
# def generate_invoice(items: List[Dict[str, Decimal]], invoice_discount: Decimal,
#                      sgst_percent: Decimal, cgst_percent: Decimal, igst_percent: Decimal) -> Dict:
#
#     products = [calculate_product_tax(item) for item in items]
#     totals = calculate_invoice_totals(products, invoice_discount, sgst_percent, cgst_percent, igst_percent)
#
#     return {
#         'products': products,
#         'totals': totals
#     }
#
#
# # Example usage
# items = [
#     {
#         'name': 'CHOCO BAR',
#         'distributor_sale': Decimal('211.54'),
#         'distributor_gst': Decimal('38.08'),
#         'carton_size': Decimal('14'),
#         'product_discount': Decimal('50'),
#         'product_quantity': Decimal('2'),
#         'gst': Decimal('18')
#     },
#     {
#         'name': 'MANGO CANDY',
#         'distributor_sale': Decimal('189.75'),
#         'distributor_gst': Decimal('34.16'),
#         'carton_size': Decimal('25'),
#         'product_discount': Decimal('50'),
#         'product_quantity': Decimal('2'),
#         'gst': Decimal('18')
#     }
# ]
#
# invoice = generate_invoice(items, Decimal('10'), Decimal('9'), Decimal('9'), Decimal('0'))

# print("Products:")
# for product in invoice['products']:
#     print(f"\n{product['name']}:")
#     for key, value in product.items():
#         if key != 'name':
#             print(f"  {key}: {value:.2f}")
#
# print("\nTotals:")
# for key, value in invoice['totals'].items():
#     print(f"{key}: {value:.2f}")





















# ========================================
# from typing import List, Dict
# from decimal import Decimal
# import json
#
#
# class DecimalEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Decimal):
#             return float(obj)
#         return super(DecimalEncoder, self).default(obj)
#
#
# def calculate_product_tax(item: Dict[str, Decimal]) -> Dict[str, Decimal]:
#     # Distributor base price calculation
#     # distributor_base_price = distributor_sale - distributor_gst
#     distributor_base_price = item['distributor_sale'] - item['distributor_gst']
#
#     # Carton base price calculation
#     # carton_base_price = distributor_base_price * carton_size
#     carton_base_price = distributor_base_price * item['carton_size']
#
#     # Discount calculation
#     # discount = carton_base_price * product_discount / 100
#     discount = carton_base_price * item['product_discount'] / Decimal('100')
#
#     # Discounted price calculation
#     # discounted_price = (carton_base_price - discount) * product_quantity
#     discounted_price = (carton_base_price - discount) * item['product_quantity']
#
#     # GST price calculation
#     # gst_price = discounted_price * gst / 100
#     gst_price = discounted_price * item['gst'] / Decimal('100')
#
#     # Total product amount calculation
#     # product_amount = discounted_price + gst_price
#     product_amount = discounted_price + gst_price
#
#     return {
#         'name': item['name'],
#         'distributor_base_price': distributor_base_price,
#         'carton_base_price': carton_base_price,
#         'discount': discount,
#         'discounted_price': discounted_price,
#         'gst_price': gst_price,
#         'product_amount': product_amount
#     }
#
#
# def calculate_invoice_totals(products: List[Dict[str, Decimal]], invoice_discount: Decimal,
#                              sgst_percent: Decimal, cgst_percent: Decimal, igst_percent: Decimal) -> Dict[str, Decimal]:
#     # Total discounted price calculation
#     # total_discounted_price = sum of all products' discounted_price
#     total_discounted_price = sum(p['discounted_price'] for p in products)
#
#     # Total GST amount calculation
#     # total_gst_amount = sum of all products' gst_price
#     total_gst_amount = sum(p['gst_price'] for p in products)
#
#     # Total product amount calculation
#     # total_product_amount = sum of all products' product_amount
#     total_product_amount = sum(p['product_amount'] for p in products)
#
#     # Invoice discounted amount calculation
#     # invoice_discounted_amount = total_discounted_price * (100 - invoice_discount) / 100
#     invoice_discounted_amount = total_discounted_price * (Decimal('100') - invoice_discount) / Decimal('100')
#
#     # SGST calculation
#     # sgst = invoice_discounted_amount * sgst_percent / 100
#     sgst = invoice_discounted_amount * sgst_percent / Decimal('100')
#
#     # CGST calculation
#     # cgst = invoice_discounted_amount * cgst_percent / 100
#     cgst = invoice_discounted_amount * cgst_percent / Decimal('100')
#
#     # IGST calculation
#     # igst = invoice_discounted_amount * igst_percent / 100
#     igst = invoice_discounted_amount * igst_percent / Decimal('100')
#
#     # Grand total calculation
#     # grand_total = invoice_discounted_amount + sgst + cgst + igst
#     grand_total = invoice_discounted_amount + sgst + cgst + igst
#
#     return {
#         'total_discounted_price': total_discounted_price,
#         'total_gst_amount': total_gst_amount,
#         'total_product_amount': total_product_amount,
#         'invoice_discounted_amount': invoice_discounted_amount,
#         'sgst': sgst,
#         'cgst': cgst,
#         'igst': igst,
#         'grand_total': grand_total
#     }
#
#
# def generate_invoice(items: List[Dict[str, Decimal]], invoice_discount: Decimal,
#                      sgst_percent: Decimal, cgst_percent: Decimal, igst_percent: Decimal) -> Dict:
#     products = [calculate_product_tax(item) for item in items]
#     totals = calculate_invoice_totals(products, invoice_discount, sgst_percent, cgst_percent, igst_percent)
#
#     return {
#         'products': products,
#         'totals': totals
#     }
#
#
# def generate_json_file(invoice: Dict, filename: str = "invoice.json"):
#     with open(filename, 'w') as f:
#         json.dump(invoice, f, indent=2, cls=DecimalEncoder)
#     print(f"JSON file generated: {filename}")
#
#
# # Example usage
# items = [
#     {
#         'name': 'CHOCO BAR',
#         'distributor_sale': Decimal('211.54'),
#         'distributor_gst': Decimal('38.08'),
#         'carton_size': Decimal('14'),
#         'product_discount': Decimal('50'),
#         'product_quantity': Decimal('2'),
#         'gst': Decimal('18')
#     },
#     {
#         'name': 'MANGO CANDY',
#         'distributor_sale': Decimal('189.75'),
#         'distributor_gst': Decimal('34.16'),
#         'carton_size': Decimal('25'),
#         'product_discount': Decimal('50'),
#         'product_quantity': Decimal('2'),
#         'gst': Decimal('18')
#     }
# ]
#
# invoice = generate_invoice(items, Decimal('10'), Decimal('9'), Decimal('9'), Decimal('0'))
# generate_json_file(invoice, "invoice_calculation.json")
#
# print("Invoice calculation completed. Check 'invoice_calculation.json' for the results.")
# ===============below
#

# from typing import List, Dict, Union
# from decimal import Decimal
# import json
#
#
# class DecimalEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Decimal):
#             return float(obj)
#         return super(DecimalEncoder, self).default(obj)
#
#
# def calculate_tax(item: Dict[str, Union[str, Decimal]]) -> Dict[str, Decimal]:
#     d = lambda x: Decimal(str(x))
#
#     base_price = item['distributor_sale']
#     discount = base_price * item['product_discount'] / d(100)
#     discounted_price = (base_price - discount) * item['product_quantity']
#     gst_price = base_price * item['gst'] / d(100) * item['product_quantity']
#     product_amount = discounted_price + gst_price
#
#     return {
#         'base_price': base_price,
#         'discount': discount,
#         'discounted_price': discounted_price,
#         'gst_price': gst_price,
#         'product_amount': product_amount
#     }
#
#
# def generate_invoice_json(items: List[Dict[str, Union[str, float]]], filename: str = "invoice.json"):
#     invoice_data = {
#         "items": [],
#         "totals": {
#             "discount": Decimal('0'),
#             "discounted_price": Decimal('0'),
#             "gst": Decimal('0'),
#             "amount": Decimal('0')
#         },
#         "additional_calculations": {}
#     }
#
#     for item in items:
#         item_decimal = {k: Decimal(str(v)) if isinstance(v, (int, float)) else v for k, v in item.items()}
#         result = calculate_tax(item_decimal)
#
#         item_data = {
#             "name": item['name'],
#             "quantity": item['product_quantity'],
#             "unit": f"Box ({item['carton_size']})",
#             "price_per_unit": result['base_price'],
#             "discount": result['discount'] * item['product_quantity'],
#             "discounted_price": result['discounted_price'],
#             "gst": result['gst_price'],
#             "amount": result['product_amount']
#         }
#         invoice_data["items"].append(item_data)
#
#         invoice_data["totals"]["discount"] += item_data['discount']
#         invoice_data["totals"]["discounted_price"] += item_data['discounted_price']
#         invoice_data["totals"]["gst"] += item_data['gst']
#         invoice_data["totals"]["amount"] += item_data['amount']
#
#     # Calculate additional values
#     sub_total = invoice_data["totals"]["discounted_price"]
#     invoice_discount = sub_total * Decimal('0.10')
#     taxable_amount = sub_total - invoice_discount
#     sgst = taxable_amount * Decimal('0.09')
#     cgst = taxable_amount * Decimal('0.09')
#     igst = taxable_amount * Decimal('0.00')
#     grand_total = taxable_amount + sgst + cgst + igst
#
#     invoice_data["additional_calculations"] = {
#         "sub_total": sub_total,
#         "invoice_discount": invoice_discount,
#         "taxable_amount": taxable_amount,
#         "sgst": sgst,
#         "cgst": cgst,
#         "igst": igst,
#         "grand_total": grand_total
#     }
#
#     # Write to JSON file
#     with open(filename, 'w') as f:
#         json.dump(invoice_data, f, indent=2, cls=DecimalEncoder)
#
#     print(f"JSON file generated: {filename}")
#
#
# # Example usage
# items = [
#     {
#         "name": "CHOCO BAR",
#         "distributor_sale": 211.54,
#         "distributor_gst": 38.08,
#         "carton_size": 14,
#         "product_discount": 50,
#         "product_quantity": 2,
#         "gst": 18,
#         "invoice_discount": 10,
#         "sgst_percent": 9,
#         "cgst_percent": 9,
#         "igst_percent": 0
#     },
#     {
#         "name": "MANGO CANDY",
#         "distributor_sale": 189.75,
#         "distributor_gst": 34.16,
#         "carton_size": 25,
#         "product_discount": 50,
#         "product_quantity": 2,
#         "gst": 18,
#         "invoice_discount": 10,
#         "sgst_percent": 9,
#         "cgst_percent": 9,
#         "igst_percent": 0
#     }
# ]
#
# generate_invoice_json(items, "invoice.json")
# # from typing import List, Dict, Union
# # from decimal import Decimal
# # import json
# #
# #
# # def calculate_tax(item: Dict[str, Union[str, Decimal]]) -> Dict[str, Decimal]:
# #     d = lambda x: Decimal(str(x))
# #
# #     base_price = item['distributor_sale']
# #     discount = base_price * item['product_discount'] / d(100)
# #     discounted_price = (base_price - discount) * item['product_quantity']
# #     gst_price = base_price * item['gst'] / d(100) * item['product_quantity']
# #     product_amount = discounted_price + gst_price
# #
# #     return {
# #         'base_price': base_price,
# #         'discount': discount,
# #         'discounted_price': discounted_price,
# #         'gst_price': gst_price,
# #         'product_amount': product_amount
# #     }
# #
# #
# # def generate_invoice_table(items: List[Dict[str, Union[str, float]]]) -> str:
# #     table_rows = []
# #     total = {
# #         'discount': Decimal('0'),
# #         'discounted_price': Decimal('0'),
# #         'gst': Decimal('0'),
# #         'amount': Decimal('0')
# #     }
# #
# #     for item in items:
# #         item_decimal = {k: Decimal(str(v)) if isinstance(v, (int, float)) else v for k, v in item.items()}
# #         result = calculate_tax(item_decimal)
# #
# #         row = {
# #             'name': item['name'],
# #             'qty': item['product_quantity'],
# #             'unit': f"Box ({item['carton_size']})",
# #             'price_per_unit': result['base_price'],
# #             'discount': result['discount'] * item['product_quantity'],
# #             'discounted_price': result['discounted_price'],
# #             'gst': result['gst_price'],
# #             'amount': result['product_amount']
# #         }
# #         table_rows.append(row)
# #
# #         total['discount'] += row['discount']
# #         total['discounted_price'] += row['discounted_price']
# #         total['gst'] += row['gst']
# #         total['amount'] += row['amount']
# #
# #     # Calculate additional values
# #     sub_total = total['discounted_price']
# #     invoice_discount = sub_total * Decimal('0.10')
# #     taxable_amount = sub_total - invoice_discount
# #     sgst = taxable_amount * Decimal('0.09')
# #     cgst = taxable_amount * Decimal('0.09')
# #     igst = taxable_amount * Decimal('0.00')
# #     grand_total = taxable_amount + sgst + cgst + igst
# #
# #     # Generate table string
# #     table = "| Item Name | Qty | Unit | Price/Unit | Discount | Discounted Price | GST 18% | Amount |\n"
# #     table += "|-----------|-----|------|------------|----------|-------------------|---------|--------|\n"
# #
# #     for row in table_rows:
# #         table += f"| {row['name']} | {row['qty']} | {row['unit']} | {row['price_per_unit']:.2f} | {row['discount']:.2f} | {row['discounted_price']:.2f} | {row['gst']:.2f} | {row['amount']:.2f} |\n"
# #
# #     table += f"| Total | | | | {total['discount']:.2f} | {total['discounted_price']:.2f} | {total['gst']:.2f} | {total['amount']:.2f} |\n\n"
# #
# #     table += f"Additional Calculations:\n"
# #     table += f"- Sub Total: {sub_total:.2f}\n"
# #     table += f"- INVOICE DISCOUNT@10.0%: {invoice_discount:.2f}\n"
# #     table += f"- SGST@9.0%: {sgst:.2f}\n"
# #     table += f"- CGST@9.0%: {cgst:.2f}\n"
# #     table += f"- IGST@0.0%: {igst:.2f}\n"
# #     table += f"- Grand Total: {grand_total:.2f}\n"
# #
# #     return table
# #
# #
# # # Example usage
# # items = [
# #     {
# #         "name": "CHOCO BAR",
# #         "distributor_sale": 211.54,
# #         "distributor_gst": 38.08,
# #         "carton_size": 14,
# #         "product_discount": 50,
# #         "product_quantity": 2,
# #         "gst": 18,
# #         "invoice_discount": 10,
# #         "sgst_percent": 9,
# #         "cgst_percent": 9,
# #         "igst_percent": 0
# #     },
# #     {
# #         "name": "MANGO CANDY",
# #         "distributor_sale": 189.75,
# #         "distributor_gst": 34.16,
# #         "carton_size": 25,
# #         "product_discount": 50,
# #         "product_quantity": 2,
# #         "gst": 18,
# #         "invoice_discount": 10,
# #         "sgst_percent": 9,
# #         "cgst_percent": 9,
# #         "igst_percent": 0
# #     }
# # ]
# #
# # print(generate_invoice_table(items))
# # def calculate_tax(distributor_sale,
# #                   distributor_gst,
# #                   carton_size,
# #                   product_discount,
# #                   product_quantity,
# #                   gst,
# #                   invoice_discount,
# #                   sgst_percent, cgst_percent, igst_percent):
# #     distributor_base_price = distributor_sale - distributor_gst
# #     carton_distributor_base_price = distributor_base_price * carton_size
# #     discount = carton_distributor_base_price * product_discount / 100
# #     discounted_price = (carton_distributor_base_price - discount) * product_quantity
# #     gst_price = discounted_price * gst / 100
# #     product_amount = discounted_price + gst_price
# #
# #     total_product_amount = sum(product_amount)
# #     total_gst_amount = sum(gst_price)
# #
# #     sub_total = sum(discounted_price)
# #     invoice_discounted_amount = sub_total - (sub_total * invoice_discount / 100)
# #
# #     sgst = invoice_discounted_amount * sgst_percent / 100
# #     cgst = invoice_discounted_amount * cgst_percent / 100
# #     igst = invoice_discounted_amount * igst_percent / 100
# #
# #     grand_total = invoice_discounted_amount + sgst + cgst + igst
# #
# #     # Return all computed values
# #     return {
# #         "distributor_base_price": distributor_base_price,
# #         "carton_distributor_base_price": carton_distributor_base_price,
# #         "discount": discount,
# #         "discounted_price": discounted_price,
# #         "gst_price": gst_price,
# #         "product_amount": product_amount,
# #         "total_product_amount": total_product_amount,
# #         "total_gst_amount": total_gst_amount,
# #         "sub_total": sub_total,
# #         "invoice_discounted_amount": invoice_discounted_amount,
# #         "sgst": sgst,
# #         "cgst": cgst,
# #         "igst": igst,
# #         "grand_total": grand_total
# #     }
# #
# #
# # # Example usage
# # result = calculate_tax(distributor_sale=500, distributor_gst=50, carton_size=5, product_discount=10,
# #                        product_quantity=2, gst=18, invoice_discount=10, sgst_percent=9,
# #                        cgst_percent=9, igst_percent=0)
# #
# # print(result)
#
# #
# # def calculate_tax(distributor_sale, distributor_gst, carton_size, product_discount,
# #                   product_quantity, gst, invoice_discount, sgst_percent, cgst_percent, igst_percent):
# #     # Calculate the base price excluding GST
# #     distributor_base_price = distributor_sale - distributor_gst
# #     print(f"Distributor Base Price: {distributor_sale} - {distributor_gst} = {distributor_base_price}")
# #
# #     # Calculate the base price for the carton
# #     carton_distributor_base_price = distributor_base_price * carton_size
# #     print(f"Carton Distributor Base Price: {distributor_base_price} * {carton_size} = {carton_distributor_base_price}")
# #
# #     # Calculate the discount on the carton base price
# #     discount = carton_distributor_base_price * product_discount / 100
# #     print(f"Discount: {carton_distributor_base_price} * {product_discount}% = {discount}")
# #
# #     # Calculate the discounted price for the total quantity
# #     discounted_price = (carton_distributor_base_price - discount) * product_quantity
# #     print(f"Discounted Price: ({carton_distributor_base_price} - {discount}) * {product_quantity} = {discounted_price}")
# #
# #     # Calculate the GST price on the discounted price
# #     gst_price = discounted_price * gst / 100
# #     print(f"GST Price: {discounted_price} * {gst}% = {gst_price}")
# #
# #     # Calculate the total product amount including GST
# #     product_amount = discounted_price + gst_price
# #     print(f"Product Amount: {discounted_price} + {gst_price} = {product_amount}")
# #
# #     # Calculate subtotal and apply invoice discount
# #     sub_total = discounted_price
# #     invoice_discounted_amount = sub_total - (sub_total * invoice_discount / 100)
# #     print(
# #         f"Invoice Discounted Amount: {sub_total} - ({sub_total} * {invoice_discount}% ) = {invoice_discounted_amount}")
# #
# #     # Calculate SGST, CGST, and IGST based on percentages
# #     sgst = invoice_discounted_amount * sgst_percent / 100
# #     cgst = invoice_discounted_amount * cgst_percent / 100
# #     igst = invoice_discounted_amount * igst_percent / 100
# #     print(f"SGST: {invoice_discounted_amount} * {sgst_percent}% = {sgst}")
# #     print(f"CGST: {invoice_discounted_amount} * {cgst_percent}% = {cgst}")
# #     print(f"IGST: {invoice_discounted_amount} * {igst_percent}% = {igst}")
# #
# #     # Calculate the grand total
# #     grand_total = invoice_discounted_amount + sgst + cgst + igst
# #     print(f"Grand Total: {invoice_discounted_amount} + {sgst} + {cgst} + {igst} = {grand_total}")
# #
# #     # Return all relevant data as a dictionary
# #     return {
# #         "distributor_base_price": distributor_base_price,
# #         "carton_distributor_base_price": carton_distributor_base_price,
# #         "discount": discount,
# #         "discounted_price": discounted_price,
# #         "gst_price": gst_price,
# #         "product_amount": product_amount,
# #         "sub_total": sub_total,
# #         "invoice_discounted_amount": invoice_discounted_amount,
# #         "sgst": sgst,
# #         "cgst": cgst,
# #         "igst": igst,
# #         "grand_total": grand_total
# #     }
# #
# #
# # # Example usage
# # result = calculate_tax(
# #     distributor_sale=10,  # Distributor Sale Price
# #     distributor_gst=2,  # Distributor GST
# #     carton_size=5,  # Size of the carton (number of units)
# #     product_discount=50,  # Discount percentage
# #     product_quantity=2,  # Quantity of cartons
# #     gst=20,  # GST percentage
# #     invoice_discount=10,  # Invoice discount percentage
# #     sgst_percent=9,  # SGST percentage
# #     cgst_percent=9,  # CGST percentage
# #     igst_percent=0  # IGST percentage
# # )
# #
# # # Print the result
# # print("\nCalculated Invoice Data:")
# # for key, value in result.items():
# #     print(f"{key}: ${value:.2f}")
# #
# # from typing import List, Dict, Union
# # import json
# # from decimal import Decimal
# #
# #
# # def calculate_tax(item: Dict[str, Union[str, Decimal]]) -> Dict[str, Decimal]:
# #     d = lambda x: Decimal(str(x))
# #
# #     base_price = item['distributor_sale'] - item['distributor_gst']
# #     carton_price = base_price * item['carton_size']
# #     discount = carton_price * item['product_discount'] / d(100)
# #     discounted_price = (carton_price - discount) * item['product_quantity']
# #     gst_price = discounted_price * item['gst'] / d(100)
# #     product_amount = discounted_price + gst_price
# #
# #     invoice_discounted = discounted_price * (d(1) - item['invoice_discount'] / d(100))
# #     sgst = invoice_discounted * item['sgst_percent'] / d(100)
# #     cgst = invoice_discounted * item['cgst_percent'] / d(100)
# #     igst = invoice_discounted * item['igst_percent'] / d(100)
# #     grand_total = invoice_discounted + sgst + cgst + igst
# #
# #     return {
# #         'discounted_price': discounted_price,
# #         'gst_price': gst_price,
# #         'product_amount': product_amount,
# #         'invoice_discounted': invoice_discounted,
# #         'sgst': sgst,
# #         'cgst': cgst,
# #         'igst': igst,
# #         'grand_total': grand_total
# #     }
# #
# #
# # def generate_invoice_json(items: List[Dict[str, Union[str, float]]]) -> str:
# #     total_results = {
# #         'items': [],
# #         'sub_total': Decimal('0'),
# #         'total_gst': Decimal('0'),
# #         'invoice_discount': Decimal('0'),
# #         'discounted_total': Decimal('0'),
# #         'sgst': Decimal('0'),
# #         'cgst': Decimal('0'),
# #         'igst': Decimal('0'),
# #         'grand_total': Decimal('0')
# #     }
# #
# #     for item in items:
# #         item_decimal = {k: Decimal(str(v)) if isinstance(v, (int, float)) else v for k, v in item.items()}
# #         result = calculate_tax(item_decimal)
# #
# #         total_results['items'].append({
# #             'name': item['name'],
# #             'amount': result['product_amount'],
# #             'gst': result['gst_price']
# #         })
# #
# #         total_results['sub_total'] += result['discounted_price']
# #         total_results['total_gst'] += result['gst_price']
# #         total_results['invoice_discount'] += result['discounted_price'] - result['invoice_discounted']
# #         total_results['discounted_total'] += result['invoice_discounted']
# #         total_results['sgst'] += result['sgst']
# #         total_results['cgst'] += result['cgst']
# #         total_results['igst'] += result['igst']
# #         total_results['grand_total'] += result['grand_total']
# #
# #     # Convert Decimal to float for JSON serialization
# #     return json.dumps({k: float(v) if isinstance(v, Decimal) else
# #     [{kk: float(vv) if isinstance(vv, Decimal) else vv for kk, vv in i.items()}
# #      for i in v] if k == 'items' else v
# #                        for k, v in total_results.items()}, indent=2)
# #
# #
# # # Example usage
# # items = [
# #     {
# #         "name": "CHOCO BAR",
# #         "distributor_sale": 211.54,
# #         "distributor_gst": 38.08,
# #         "carton_size": 14,
# #         "product_discount": 50,
# #         "product_quantity": 2,
# #         "gst": 18,
# #         "invoice_discount": 10,
# #         "sgst_percent": 9,
# #         "cgst_percent": 9,
# #         "igst_percent": 0
# #     },
# #     {
# #         "name": "MANGO CANDY",
# #         "distributor_sale": 189.75,
# #         "distributor_gst": 34.16,
# #         "carton_size": 25,
# #         "product_discount": 50,
# #         "product_quantity": 2,
# #         "gst": 18,
# #         "invoice_discount": 10,
# #         "sgst_percent": 9,
# #         "cgst_percent": 9,
# #         "igst_percent": 0
# #     }
# # ]
# #
# # print(generate_invoice_json(items))
# #
# # import json
# #
# #
# # def calculate_tax(distributor_sale, distributor_gst, carton_size, product_discount,
# #                   product_quantity, gst, invoice_discount, sgst_percent, cgst_percent, igst_percent):
# #     # Calculate the base price excluding GST
# #     distributor_base_price = distributor_sale - distributor_gst
# #     print(f"Distributor Base Price: {distributor_sale} - {distributor_gst} = {distributor_base_price}")
# #
# #     # Calculate the base price for the carton
# #     carton_distributor_base_price = distributor_base_price * carton_size
# #     print(f"Carton Distributor Base Price: {distributor_base_price} * {carton_size} = {carton_distributor_base_price}")
# #
# #     # Calculate the discount on the carton base price
# #     discount = carton_distributor_base_price * product_discount / 100
# #     print(f"Discount: {carton_distributor_base_price} * {product_discount}% = {discount}")
# #
# #     # Calculate the discounted price for the total quantity
# #     discounted_price = (carton_distributor_base_price - discount) * product_quantity
# #     print(f"Discounted Price: ({carton_distributor_base_price} - {discount}) * {product_quantity} = {discounted_price}")
# #
# #     # Calculate the GST price on the discounted price
# #     gst_price = discounted_price * gst / 100
# #     print(f"GST Price: {discounted_price} * {gst}% = {gst_price}")
# #
# #     # Calculate the total product amount including GST
# #     product_amount = discounted_price + gst_price
# #     print(f"Product Amount: {discounted_price} + {gst_price} = {product_amount}")
# #
# #     # Calculate subtotal and apply invoice discount
# #     sub_total = discounted_price
# #     invoice_discounted_amount = sub_total - (sub_total * invoice_discount / 100)
# #     print(
# #         f"Invoice Discounted Amount: {sub_total} - ({sub_total} * {invoice_discount}% ) = {invoice_discounted_amount}")
# #
# #     # Calculate SGST, CGST, and IGST based on percentages
# #     sgst = invoice_discounted_amount * sgst_percent / 100
# #     cgst = invoice_discounted_amount * cgst_percent / 100
# #     igst = invoice_discounted_amount * igst_percent / 100
# #     print(f"SGST: {invoice_discounted_amount} * {sgst_percent}% = {sgst}")
# #     print(f"CGST: {invoice_discounted_amount} * {cgst_percent}% = {cgst}")
# #     print(f"IGST: {invoice_discounted_amount} * {igst_percent}% = {igst}")
# #
# #     # Calculate the grand total
# #     grand_total = invoice_discounted_amount + sgst + cgst + igst
# #     print(f"Grand Total: {invoice_discounted_amount} + {sgst} + {cgst} + {igst} = {grand_total}")
# #
# #     # Return all relevant data as a dictionary
# #     return {
# #         "distributor_base_price": distributor_base_price,
# #         "carton_distributor_base_price": carton_distributor_base_price,
# #         "discount": discount,
# #         "discounted_price": discounted_price,
# #         "gst_price": gst_price,
# #         "product_amount": product_amount,
# #         "sub_total": sub_total,
# #         "invoice_discounted_amount": invoice_discounted_amount,
# #         "sgst": sgst,
# #         "cgst": cgst,
# #         "igst": igst,
# #         "grand_total": grand_total
# #     }
# #
# #
# # def generate_invoice_json(items):
# #     total_results = {
# #         "items": [],
# #         "sub_total": 0,
# #         "total_gst": 0,
# #         "invoice_discount": 0,
# #         "discounted_total": 0,
# #         "sgst": 0,
# #         "cgst": 0,
# #         "igst": 0,
# #         "grand_total": 0
# #     }
# #
# #     for item in items:
# #         result = calculate_tax(**item)
# #
# #         total_results["items"].append({
# #             "name": item.get("name", "Unknown Item"),
# #             "amount": result["product_amount"],
# #             "gst": result["gst_price"]
# #         })
# #
# #         total_results["sub_total"] += result["discounted_price"]
# #         total_results["total_gst"] += result["gst_price"]
# #         total_results["invoice_discount"] += result["sub_total"] - result["invoice_discounted_amount"]
# #         total_results["discounted_total"] += result["invoice_discounted_amount"]
# #         total_results["sgst"] += result["sgst"]
# #         total_results["cgst"] += result["cgst"]
# #         total_results["igst"] += result["igst"]
# #         total_results["grand_total"] += result["grand_total"]
# #
# #     # Round all numeric values to 2 decimal places
# #     for key, value in total_results.items():
# #         if isinstance(value, (int, float)):
# #             total_results[key] = round(value, 2)
# #         elif isinstance(value, list):
# #             for item in value:
# #                 for k, v in item.items():
# #                     if isinstance(v, (int, float)):
# #                         item[k] = round(v, 2)
# #
# #     return json.dumps(total_results, indent=2)
# #
# #
# # # Example usage
# # items = [
# #     {
# #         "name": "CHOCO BAR",
# #         "distributor_sale": 211.54,
# #         "distributor_gst": 38.08,
# #         "carton_size": 14,
# #         "product_discount": 50,
# #         "product_quantity": 2,
# #         "gst": 18,
# #         "invoice_discount": 10,
# #         "sgst_percent": 9,
# #         "cgst_percent": 9,
# #         "igst_percent": 0
# #     },
# #     {
# #         "name": "MANGO CANDY",
# #         "distributor_sale": 189.75,
# #         "distributor_gst": 34.16,
# #         "carton_size": 25,
# #         "product_discount": 50,
# #         "product_quantity": 2,
# #         "gst": 18,
# #         "invoice_discount": 10,
# #         "sgst_percent": 9,
# #         "cgst_percent": 9,
# #         "igst_percent": 0
# #     }
# # ]
# #
# # print(generate_invoice_json(items))