from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import RetailerMainOrders
from .invoice_utils import generate_invoice


@api_view(['GET'])
def calculate_invoice_api(request, order_id):
    order = get_object_or_404(RetailerMainOrders, id=order_id)

    # Generate invoice data
    invoice_data = generate_invoice(order)

    return Response(invoice_data, status=status.HTTP_200_OK)
"""
# distributors/invoice_utils.py

from decimal import Decimal


def calculate_product_tax(order_item):
    # Convert all relevant fields to Decimal for precise calculations
    distributor_sale = Decimal(str(order_item.distributor_sale))
    distributor_gst = Decimal(str(order_item.distributor_gst))
    carton_size = Decimal(str(order_item.carton_size))
    product_discount = Decimal(str(order_item.product_id.product_discount))
    quantity = Decimal(str(order_item.quantity))
    gst_rate = Decimal(str(order_item.gst))

    # Formula: Distributor Base Price = Distributor Sale Price - Distributor GST
    distributor_base_price = distributor_sale - distributor_gst

    # Formula: Carton Base Price = Distributor Base Price * Carton Size
    carton_base_price = round((distributor_base_price * carton_size),2)

    # Formula: Discount = Carton Base Price * Product Discount
    discount = round(carton_base_price * (product_discount / Decimal('100')),2)
    discount_amount = round(carton_base_price * (product_discount / Decimal('100')) * quantity,2)

    # Formula: Discounted Price = (Carton Base Price - Discount) * Product Quantity
    discounted_price = (carton_base_price - discount) * quantity

    # Formula: GST Price = Discounted Price * GST Rate
    gst_price = round(discounted_price * (gst_rate / Decimal('100')))

    # Formula: Product Amount = Discounted Price + GST Price
    product_amount = discounted_price + gst_price

    # Update the order item with calculated values
    order_item.distributor_margin_price = distributor_sale - distributor_base_price
    order_item.sum = discounted_price
    order_item.CGST = gst_price / 2  # Splitting GST equally between CGST and SGST
    order_item.SGST = gst_price / 2
    order_item.IGST = Decimal('0')  # Set to 0 for intra-state transactions
    order_item.amount = product_amount
    order_item.save()

    return {
        'name': order_item.product_name,
        'distributor_base_price': round(distributor_base_price, 2),
        'carton_base_price': round(carton_base_price, 2),
        'quantity': quantity,
        'carton_size': carton_size,
        'discount': round(discount, 2),
        'product_discount': product_discount,
        'discount_amount': discount_amount,
        'discounted_price': round(discounted_price, 2),
        'gst_price': round(gst_price, 2),
        'product_amount': round(product_amount, 2)
    }


def calculate_invoice_totals(main_order):
    order_items = main_order.retailer_orders1.all()

    # Initialize totals
    total_discounted_price = Decimal('0')
    total_gst_amount = Decimal('0')
    total_product_amount = Decimal('0')

    # Calculate totals by iterating through order items
    for item in order_items:
        # Recalculate the discounted price for each item
        distributor_sale = Decimal(str(item.distributor_sale))
        distributor_gst = Decimal(str(item.distributor_gst))
        carton_size = Decimal(str(item.carton_size))
        product_discount = Decimal(str(item.product_id.product_discount))
        quantity = Decimal(str(item.quantity))

        distributor_base_price = distributor_sale - distributor_gst
        carton_base_price = distributor_base_price * carton_size
        discount =round( carton_base_price * (product_discount / Decimal('100')),2)
        discounted_price = round((carton_base_price - discount) * quantity,2)

        # Formula: Total Discounted Price = Sum of all items' Discounted Prices
        total_discounted_price += discounted_price

        # Formula: Total GST Amount = Sum of all items' GST Amounts
        total_gst_amount += Decimal(str(item.CGST)) + Decimal(str(item.SGST)) + Decimal(str(item.IGST))

        # Formula: Total Product Amount = Sum of all items' Product Amounts
        total_product_amount += Decimal(str(item.amount))

    # Convert other relevant fields to Decimal
    discount_percentage = Decimal(str(main_order.discount_percentage))
    sgst_rate = Decimal(str(main_order.SGST_rate))
    cgst_rate = Decimal(str(main_order.CGST_rate))
    igst_rate = Decimal(str(main_order.IGST_rate))

    # Formula: Invoice Discounted Amount = Total Discounted Price * (100% - Invoice Discount)
    invoice_discounted_amount = total_discounted_price * (Decimal('100') - discount_percentage) / Decimal('100')

    invoice_discount_amount = total_discounted_price * ( discount_percentage / Decimal('100'))

    # Calculate GST based on the discounted amount
    sgst = invoice_discounted_amount * (sgst_rate / Decimal('100'))
    cgst = invoice_discounted_amount * (cgst_rate / Decimal('100'))
    igst = invoice_discounted_amount * (igst_rate / Decimal('100'))

    # Recalculate total GST amount
    total_gst_amount = sgst + cgst + igst

    # Formula: Grand Total = Invoice Discounted Amount + Total GST Amount
    grand_total = invoice_discounted_amount + total_gst_amount

    # Update main order with calculated values
    main_order.sub_total = total_discounted_price
    main_order.CGST = cgst
    main_order.SGST = sgst
    main_order.IGST = igst
    main_order.gst = total_gst_amount
    main_order.grand_total = grand_total
    main_order.pending_amount = grand_total
    main_order.save()

    return {
        'generated_by': main_order.distributor.email if main_order.distributor.email else f"{main_order.distributor.first_name}{main_order.distributor.last_name}",
        'total_discounted_price': round(total_discounted_price, 2),
        'total_gst_amount': round(total_gst_amount, 2),
        'total_product_amount': round(total_product_amount, 2),
        'invoice_discounted_amount': round(invoice_discounted_amount, 2),
        'discount_percentage': discount_percentage,
        'invoice_discount_amount': round(invoice_discount_amount,2),
        'sgst': round(sgst, 2),
        'cgst': round(cgst, 2),
        'igst': round(igst, 2),
        'sgst_rate': sgst_rate,
        'cgst_rate': cgst_rate,
        'igst_rate': igst_rate,
        'grand_total': round(grand_total, 2)
    }


def generate_invoice(main_order):
    order_items = main_order.retailer_orders1.all()

    products = [calculate_product_tax(item) for item in order_items]
    totals = calculate_invoice_totals(main_order)

    return {
        'products': products,
        'totals': totals
    }



# # distributors/invoice_utils.py
#
# from decimal import Decimal
#
#
# def calculate_product_tax(order_item):
#     # Convert all relevant fields to Decimal for precise calculations
#     distributor_sale = Decimal(str(order_item.distributor_sale))
#     distributor_gst = Decimal(str(order_item.distributor_gst))
#     carton_size = Decimal(str(order_item.carton_size))
#     product_discount = Decimal(str(order_item.product_id.product_discount))
#     quantity = Decimal(str(order_item.quantity))
#     gst_rate = Decimal(str(order_item.gst))
#
#     # Formula: Distributor Base Price = Distributor Sale Price - Distributor GST
#     distributor_base_price = distributor_sale - distributor_gst
#
#     # Formula: Carton Base Price = Distributor Base Price * Carton Size
#     carton_base_price = distributor_base_price * carton_size
#
#     # Formula: Discount = Carton Base Price * Product Discount
#     discount = carton_base_price * (product_discount / Decimal('100'))
#
#     # Formula: Discounted Price = (Carton Base Price - Discount) * Product Quantity
#     discounted_price = (carton_base_price - discount) * quantity
#
#     # Formula: GST Price = Discounted Price * GST Rate
#     gst_price = discounted_price * (gst_rate / Decimal('100'))
#
#     # Formula: Product Amount = Discounted Price + GST Price
#     product_amount = discounted_price + gst_price
#
#     # Update the order item with calculated values
#     order_item.distributor_margin_price = distributor_sale - distributor_base_price
#     order_item.sum = discounted_price
#     order_item.CGST = gst_price / 2  # Splitting GST equally between CGST and SGST
#     order_item.SGST = gst_price / 2
#     order_item.IGST = Decimal('0')  # Set to 0 for intra-state transactions
#     order_item.amount = product_amount
#     order_item.save()
#
#     return {
#         'name': order_item.product_name,
#         'distributor_base_price': round(distributor_base_price, 2),
#         'carton_base_price': round(carton_base_price, 2),
#         'quantity': quantity,
#         'carton_size': carton_size,
#         'discount': round(discount, 2),
#         'product_discount': product_discount,
#         'discounted_price': round(discounted_price, 2),
#         'gst_price': round(gst_price, 2),
#         'product_amount': round(product_amount, 2)
#     }
#
#
# def calculate_invoice_totals(main_order):
#     order_items = main_order.retailer_orders1.all()
#
#     # Initialize totals
#     total_discounted_price = Decimal('0')
#     total_gst_amount = Decimal('0')
#     total_product_amount = Decimal('0')
#
#     # Calculate totals by iterating through order items
#     for item in order_items:
#         # Formula: Total Discounted Price = Sum of all items' Discounted Prices
#         total_discounted_price += Decimal(str(item.sum))
#
#         # Formula: Total GST Amount = Sum of all items' GST Amounts
#         total_gst_amount += Decimal(str(item.CGST)) + Decimal(str(item.SGST)) + Decimal(str(item.IGST))
#
#         # Formula: Total Product Amount = Sum of all items' Product Amounts
#         total_product_amount += Decimal(str(item.amount))
#
#     # Convert other relevant fields to Decimal
#     discount_percentage = Decimal(str(main_order.discount_percentage))
#     sgst_rate = Decimal(str(main_order.SGST_rate))
#     cgst_rate = Decimal(str(main_order.CGST_rate))
#     igst_rate = Decimal(str(main_order.IGST_rate))
#
#     # Formula: Invoice Discounted Amount = Total Discounted Price * (100% - Invoice Discount)
#     invoice_discounted_amount = total_discounted_price * (Decimal('100') - discount_percentage) / Decimal('100')
#
#     # Formula: SGST = Invoice Discounted Amount * SGST Rate
#     sgst = invoice_discounted_amount * (sgst_rate / Decimal('100'))
#
#     # Formula: CGST = Invoice Discounted Amount * CGST Rate
#     cgst = invoice_discounted_amount * (cgst_rate / Decimal('100'))
#
#     # Formula: IGST = Invoice Discounted Amount * IGST Rate
#     igst = invoice_discounted_amount * (igst_rate / Decimal('100'))
#
#     # Formula: Grand Total = Invoice Discounted Amount + SGST + CGST + IGST
#     grand_total = invoice_discounted_amount + sgst + cgst + igst
#
#     # Update main order with calculated values
#     main_order.sub_total = total_product_amount
#     main_order.CGST = cgst
#     main_order.SGST = sgst
#     main_order.IGST = igst
#     main_order.gst = total_gst_amount
#     main_order.grand_total = grand_total
#     main_order.pending_amount = grand_total
#     main_order.save()
#
#     return {
#         'generated_by': main_order.distributor.email if main_order.distributor.email else f"{main_order.distributor.first_name}{main_order.distributor.last_name}",
#         'total_discounted_price': round(total_discounted_price, 2),
#         'total_gst_amount': round(total_gst_amount, 2),
#         'total_product_amount': round(total_product_amount, 2),
#         'invoice_discounted_amount': round(invoice_discounted_amount, 2),
#         'discount_percentage': discount_percentage,
#         'sgst': round(sgst, 2),
#         'cgst': round(cgst, 2),
#         'igst': round(igst, 2),
#         'sgst_rate': sgst_rate,
#         'cgst_rate': cgst_rate,
#         'igst_rate': igst_rate,
#         'grand_total': round(grand_total, 2)
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
# # distributors/invoice_utils.py
#
# from decimal import Decimal
#
# def calculate_product_tax(order_item):
#     # Convert all relevant fields to Decimal
#     distributor_sale = Decimal(str(order_item.distributor_sale))
#     distributor_gst = Decimal(str(order_item.distributor_gst))
#     carton_size = Decimal(str(order_item.carton_size))
#     product_discount = Decimal(str(order_item.product_id.product_discount))
#     quantity = Decimal(str(order_item.quantity))
#     gst_rate = Decimal(str(order_item.gst))
#
#     distributor_base_price = distributor_sale - distributor_gst
#     carton_base_price = distributor_base_price * carton_size
#     discount = carton_base_price * (product_discount / Decimal('100'))
#     discounted_price = (carton_base_price - discount) * quantity
#     gst_price = discounted_price * (gst_rate / Decimal('100'))
#     product_amount = discounted_price + gst_price
#
#     # Update the order item with calculated values
#     order_item.distributor_margin_price = distributor_sale - distributor_base_price
#     order_item.sum = discounted_price
#     order_item.CGST = gst_price / 2
#     order_item.SGST = gst_price / 2
#     order_item.IGST = Decimal('0')
#     order_item.amount = product_amount
#     order_item.save()
#
#     return {
#         'name': order_item.product_name,
#         'distributor_base_price': round(distributor_base_price, 2),
#         'carton_base_price': round(carton_base_price, 2),
#         'quantity': quantity,
#         'carton_size': carton_size,
#         'discount': round(discount, 2),
#         'product_discount': product_discount,
#         'discounted_price': round(discounted_price, 2),
#         'gst_price': round(gst_price, 2),
#         'product_amount': round(product_amount, 2)
#     }
#
# def calculate_invoice_totals(main_order):
#     order_items = main_order.retailer_orders1.all()
#
#     # Initialize totals
#     total_discounted_price = Decimal('0')
#     total_gst_amount = Decimal('0')
#     total_product_amount = Decimal('0')
#
#     # Calculate totals by iterating through order items
#     for item in order_items:
#         total_discounted_price += Decimal(str(item.sum))
#         total_gst_amount += Decimal(str(item.CGST)) + Decimal(str(item.SGST)) + Decimal(str(item.IGST))
#         total_product_amount += Decimal(str(item.amount))
#
#     # Convert other relevant fields to Decimal
#     discount_percentage = Decimal(str(main_order.discount_percentage))
#     sgst_rate = Decimal(str(main_order.SGST_rate))
#     cgst_rate = Decimal(str(main_order.CGST_rate))
#     igst_rate = Decimal(str(main_order.IGST_rate))
#
#     invoice_discounted_amount = total_discounted_price * (Decimal('100') - discount_percentage) / Decimal('100')
#
#     sgst = invoice_discounted_amount * (sgst_rate / Decimal('100'))
#     cgst = invoice_discounted_amount * (cgst_rate / Decimal('100'))
#     igst = invoice_discounted_amount * (igst_rate / Decimal('100'))
#
#     grand_total = invoice_discounted_amount + sgst + cgst + igst
#
#     # Update main order with calculated values
#     main_order.sub_total = total_product_amount
#     main_order.CGST = cgst
#     main_order.SGST = sgst
#     main_order.IGST = igst
#     main_order.gst = total_gst_amount
#     main_order.grand_total = grand_total
#     main_order.pending_amount = grand_total
#     main_order.save()
#
#     return {
#         'generated_by': main_order.distributor.email if main_order.distributor.email else f"{main_order.distributor.first_name}{main_order.distributor.last_name}",
#         'total_discounted_price': round(total_discounted_price, 2),
#         'total_gst_amount': round(total_gst_amount, 2),
#         'total_product_amount': round(total_product_amount, 2),
#         'invoice_discounted_amount': round(invoice_discounted_amount, 2),
#         'discount_percentage': discount_percentage,
#         'sgst': round(sgst, 2),
#         'cgst': round(cgst, 2),
#         'igst': round(igst, 2),
#         'sgst_rate': sgst_rate,
#         'cgst_rate': cgst_rate,
#         'igst_rate': igst_rate,
#         'grand_total': round(grand_total, 2)
#     }
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
# ====================
# # distributors/invoice_utils.py
#
# from decimal import Decimal
# from django.db.models import Sum, F
#
#
# def calculate_product_tax(order_item):
#     # Convert all relevant fields to Decimal
#     distributor_sale = Decimal(str(order_item.distributor_sale))
#     distributor_gst = Decimal(str(order_item.distributor_gst))
#     carton_size = Decimal(str(order_item.carton_size))
#     product_discount = Decimal(str(order_item.product_id.product_discount))
#     quantity = Decimal(str(order_item.quantity))
#     gst_rate = Decimal(str(order_item.gst))
#
#     distributor_base_price = distributor_sale - distributor_gst
#     carton_base_price = distributor_base_price * carton_size
#     discount = carton_base_price * (product_discount / Decimal('100'))
#     discounted_price = (carton_base_price - discount) * quantity
#     gst_price = discounted_price * (gst_rate / Decimal('100'))
#     product_amount = discounted_price + gst_price
#
#     # Update the order item with calculated values
#     order_item.distributor_margin_price = distributor_sale - distributor_base_price
#     order_item.sum = discounted_price
#     order_item.CGST = gst_price / 2
#     order_item.SGST = gst_price / 2
#     order_item.IGST = Decimal('0')
#     order_item.amount = product_amount
#     order_item.save()
#
#     return {
#         'name': order_item.product_name,
#         'distributor_base_price': round(distributor_base_price,2),
#         'carton_base_price': round(carton_base_price,2),
#         'quantity': quantity,
#         'carton_size': carton_size,
#         'discount': discount,
#         'product_discount': product_discount,
#         'discounted_price': round(discounted_price,2),
#         'gst_price': round(gst_price,2),
#         'product_amount': round(product_amount,2)
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
#     # Convert all relevant fields to Decimal
#     total_discounted_price = Decimal(str(totals['total_discounted_price'] or 0))
#     discount_percentage = Decimal(str(main_order.discount_percentage))
#     sgst_rate = Decimal(str(main_order.SGST_rate))
#     cgst_rate = Decimal(str(main_order.CGST_rate))
#     igst_rate = Decimal(str(main_order.IGST_rate))
#
#     invoice_discounted_amount = total_discounted_price * (Decimal('100') - discount_percentage) / Decimal('100')
#
#     sgst = invoice_discounted_amount * (sgst_rate / Decimal('100'))
#     cgst = invoice_discounted_amount * (cgst_rate / Decimal('100'))
#     igst = invoice_discounted_amount * (igst_rate / Decimal('100'))
#
#     grand_total = invoice_discounted_amount + sgst + cgst + igst
#
#     # Update main order with calculated values
#     main_order.sub_total = Decimal(str(totals['total_product_amount'] or 0))
#     main_order.CGST = cgst
#     main_order.SGST = sgst
#     main_order.IGST = igst
#     main_order.gst = Decimal(str(totals['total_gst_amount'] or 0))
#     main_order.grand_total = grand_total
#     main_order.pending_amount = grand_total
#     main_order.save()
#
#     return {
#         'generated_by':main_order.distributor.email if main_order.distributor.email else f"{main_order.distributor.first_name}{main_order.distributor.last_name}",
#         'total_discounted_price': round(total_discounted_price,2),
#         'total_gst_amount': round(totals['total_gst_amount'],2),
#         'total_product_amount': round(totals['total_product_amount'],2),
#         'invoice_discounted_amount': round(invoice_discounted_amount,2),
#         'discount_percentage': discount_percentage,
#         'sgst': round(sgst,2),
#         'cgst': round(cgst,2),
#         'igst': round(igst,2),
#         'sgst_rate': sgst_rate,
#         'cgst_rate': cgst_rate,
#         'igst_rate': igst_rate,
#
#         'grand_total': round(grand_total,2)
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
# # distributors/invoice_utils.py
#
# from decimal import Decimal
# from django.db.models import Sum, F
#
# from distributors.models import RetailerMainOrders
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
#
#
# # print("Products:")
# # for product in invoice['products']:
# #     print(f"\n{product['name']}:")
# #     for key, value in product.items():
# #         if key != 'name':
# #             print(f"  {key}: {value:.2f}")
# #
# # print("\nTotals:")
# # for key, value in invoice['totals'].items():
# #     print(f"{key}: {value:.2f}")
# # # Example usage
# # def process_order():
# #     try:
# #         main_order = RetailerMainOrders.objects.filter(id=7).first()
# #         invoice = generate_invoice(main_order)
# #         return invoice
# #     except RetailerMainOrders.DoesNotExist:
# #         return {"error": "Order not found"}
# # process_order()
"""