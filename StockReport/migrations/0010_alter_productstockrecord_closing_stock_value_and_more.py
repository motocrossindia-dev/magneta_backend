# Generated by Django 4.2 on 2024-10-04 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StockReport', '0009_alter_openingstock_closing_stock_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productstockrecord',
            name='closing_stock_value',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='production_value',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='sales_value',
            field=models.FloatField(default=0),
        ),
    ]
