from accounts.models import UserBase
from sales.models import retailerTransactionDetails


def retailerSalesAmountTransfer(request):
    "retailerTransactionDetails"
    retailer_id = request.GET.get('retailer_id')
    amount = request.GET.get('amount')

    retailer = UserBase.objects.get(pk=retailer_id)
    # new_transaction = retailerTransactionDetails.objects.create(retailer=retailer, amount=amount)
    transaction, created = retailerTransactionDetails.objects.get_or_create(retailer=retailer)
    if created:
        transaction.amount = amount
        transaction.totalSaleAmount = amount
        transaction.save()
    else:
        transaction.amount = transaction.amount + amount
        transaction.totalSaleAmount = transaction.totalSaleAmount + amount
        transaction.save()
    return True
