# Generated by Django 4.2 on 2024-10-04 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StockReport', '0010_alter_productstockrecord_closing_stock_value_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productstockrecord',
            name='opening_stock_value',
            field=models.FloatField(default=0),
        ),
    ]
