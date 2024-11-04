from decimal import Decimal


def calculate_product_tax(order_item, mode_of_payment):
    # Check if it's a free sample or STN
    is_free = mode_of_payment.lower() in ['free sample', 'stn']
    
    # Convert all relevant fields to Decimal for precise calculations
    distributor_sale = Decimal('0') if is_free else Decimal(str(order_item.distributor_sale))
    distributor_gst = Decimal('0') if is_free else Decimal(str(order_item.distributor_gst))
    carton_size = Decimal(str(order_item.carton_size))
    product_discount = Decimal('0') if is_free else Decimal(str(order_item.product_id.product_discount))
    quantity = Decimal(str(order_item.quantity))
    gst_rate = Decimal('0') if is_free else Decimal(str(order_item.gst))

    # Formula: Distributor Base Price = Distributor Sale Price - Distributor GST
    distributor_base_price = distributor_sale - distributor_gst

    # Formula: Carton Base Price = Distributor Base Price * Carton Size
    carton_base_price = round((distributor_base_price * carton_size), 2)

    # Formula: Discount = Carton Base Price * Product Discount
    discount = round(carton_base_price * (product_discount / Decimal('100')), 2)
    discount_amount = round(carton_base_price * (product_discount / Decimal('100')) * quantity, 2)

    # Formula: Discounted Price = (Carton Base Price - Discount) * Product Quantity
    discounted_price = (carton_base_price - discount) * quantity

    # Formula: GST Price = Discounted Price * GST Rate
    gst_price = round(discounted_price * (gst_rate / Decimal('100')))

    # Formula: Product Amount = Discounted Price + GST Price
    product_amount = discounted_price + gst_price

    # Update the order item with calculated values
    order_item.distributor_margin_price = Decimal('0') if is_free else (distributor_sale - distributor_base_price)
    order_item.sum = Decimal('0') if is_free else discounted_price
    order_item.CGST = Decimal('0') if is_free else (gst_price / 2)  # Splitting GST equally between CGST and SGST
    order_item.SGST = Decimal('0') if is_free else (gst_price / 2)
    order_item.IGST = Decimal('0')  # Set to 0 for intra-state transactions
    order_item.amount = Decimal('0') if is_free else product_amount
    order_item.save()

    return {
        'name': order_item.product_name,
        'distributor_base_price': Decimal('0') if is_free else round(distributor_base_price, 2),
        'carton_base_price': Decimal('0') if is_free else round(carton_base_price, 2),
        'quantity': quantity,
        'carton_size': carton_size,
        'discount': Decimal('0') if is_free else round(discount, 2),
        'product_discount': Decimal('0') if is_free else product_discount,
        'discount_amount': Decimal('0') if is_free else discount_amount,
        'discounted_price': Decimal('0') if is_free else round(discounted_price, 2),
        'gst_price': Decimal('0') if is_free else round(gst_price, 2),
        'product_amount': Decimal('0') if is_free else round(product_amount, 2)
    }


def calculate_invoice_totals(main_order):
    order_items = main_order.retailer_orders1.all()
    mode_of_payment = main_order.mode_of_payment.lower()
    is_free = mode_of_payment in ['free sample', 'stn']

    # If free sample or STN, set all monetary values to 0
    if is_free:
        main_order.sub_total = Decimal('0')
        main_order.CGST = Decimal('0')
        main_order.SGST = Decimal('0')
        main_order.IGST = Decimal('0')
        main_order.gst = Decimal('0')
        main_order.grand_total = Decimal('0')
        main_order.pending_amount = Decimal('0')
        main_order.save()

        return {
            'generated_by': main_order.distributor.email if main_order.distributor.email else f"{main_order.distributor.first_name}{main_order.distributor.last_name}",
            'total_discounted_price': Decimal('0'),
            'total_gst_amount': Decimal('0'),
            'total_product_amount': Decimal('0'),
            'invoice_discounted_amount': Decimal('0'),
            'discount_percentage': Decimal('0'),
            'invoice_discount_amount': Decimal('0'),
            'sgst': Decimal('0'),
            'cgst': Decimal('0'),
            'igst': Decimal('0'),
            'sgst_rate': Decimal('0'),
            'cgst_rate': Decimal('0'),
            'igst_rate': Decimal('0'),
            'grand_total': Decimal('0')
        }

    # Initialize totals for normal payment modes
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
        discount = round(carton_base_price * (product_discount / Decimal('100')), 2)
        discounted_price = round((carton_base_price - discount) * quantity, 2)

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

    invoice_discount_amount = total_discounted_price * (discount_percentage / Decimal('100'))

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
        'invoice_discount_amount': round(invoice_discount_amount, 2),
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
    mode_of_payment = main_order.mode_of_payment.lower()

    products = [calculate_product_tax(item, mode_of_payment) for item in order_items]
    totals = calculate_invoice_totals(main_order)

    return {
        'products': products,
        'totals': totals
    }
