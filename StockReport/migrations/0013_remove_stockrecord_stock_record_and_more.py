# Generated by Django 4.2 on 2024-10-04 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_product_discount'),
        ('StockReport', '0012_productstockrecord_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockrecord',
            name='stock_record',
        ),
        migrations.AddField(
            model_name='productstockrecord',
            name='stock_record',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='product_stock_records', to='StockReport.stockrecord'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='productstockrecord',
            unique_together={('product', 'stock_record')},
        ),
    ]