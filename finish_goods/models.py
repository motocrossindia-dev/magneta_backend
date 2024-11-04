# from django.db import models
#
# from inventory.models import StoreGRN
# from process_store.models import ProcessStore
#
#
# # Create your models here.
# class finishgoods(models.Model):
#     goods_store=models.ForeignKey(StoreGRN,on_delete=models.CASCADE)
#     process_store=models.ForeignKey(ProcessStore,on_delete=models.CASCADE)
#     quantity=models.IntegerField()
#     description=models.CharField(max_length=100)