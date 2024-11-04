from django.contrib import admin

from sales.models import distributor_sales, salesPerson_orders, retailerTransactionDetails, salesRetailerTransactions, \
    salesPersonCashInHand, transactionFromSalesToDistributor, ProductDiscount


class salesPersonCashInHandAdmin(admin.ModelAdmin):
    list_display = ('sales_person', 'cash_in_hand', 'amount_transferred_to_distributer', 'total')

class salesRetailerTransactionsAdmin(admin.ModelAdmin):
    list_display = ('distributor', 'sales_person', 'transaction_amount', 'mode_of_payment', 'created')
    fields =('distributor', 'sales_person', 'transaction_amount', 'mode_of_payment', 'created')

admin.site.register(distributor_sales)
admin.site.register(salesPerson_orders)
admin.site.register(retailerTransactionDetails)
admin.site.register(salesRetailerTransactions,salesRetailerTransactionsAdmin)
admin.site.register(salesPersonCashInHand,salesPersonCashInHandAdmin)
admin.site.register(transactionFromSalesToDistributor)
admin.site.register(ProductDiscount)
