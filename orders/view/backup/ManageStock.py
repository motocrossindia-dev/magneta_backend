import logging
from django.shortcuts import get_object_or_404
from distributors.models import DistributorStock, RetailerOrders
from orders.models import Order

logger = logging.getLogger("magneta_logger")


def add_stock(main_order):
    print("in add stock")
    try:
        ordered_products = Order.objects.filter(main_order=main_order)

        for ordered_product in ordered_products:
            # Try to retrieve existing DistributorStock object
            try:
                product_stock = DistributorStock.objects.get(distributor_id=main_order.distributor,
                                                             product_id=ordered_product.product_name)
            except DistributorStock.DoesNotExist:
                product_stock = None

            if product_stock is None:
                # Create new DistributorStock entry if it doesn't exist
                new_stock = DistributorStock.objects.create(product_id=ordered_product.product_name,
                                                            distributor_id=main_order.distributor,
                                                            quantity=ordered_product.accepted_quantity)
                new_stock.save()
            else:
                # Update existing DistributorStock entry
                product_stock.quantity += ordered_product.accepted_quantity
                product_stock.save()

        logger.info(f"Stock updated for Main Order {main_order.id}")
    except Exception as e:
        logger.error(f"Exception occurred in add_stock: {str(e)}")
        return str(e)


def reduce_stock(main_order):
    try:
        sold_products = RetailerOrders.objects.filter(retailer_main_order=main_order)

        for sold_product in sold_products:
            # Try to retrieve existing DistributorStock object
            try:
                product_stock = DistributorStock.objects.get(distributor_id=main_order.distributor,
                                                             product_id=sold_product.product_id)
            except DistributorStock.DoesNotExist:
                product_stock = None

            if product_stock is None:
                logger.error(f"You are trying to reduce product quantity which is not present in the distributor"
                             f" stock list")
            else:
                # Update existing DistributorStock entry
                product_stock.quantity -= sold_product.quantity
                product_stock.save()

        logger.info(f"Stock updated for Main Order {main_order.id}")
    except Exception as e:
        logger.error(f"Exception occurred in add_stock: {str(e)}")
        return str(e)
