# Generated by Django 4.2 on 2024-10-02 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StockReport', '0006_remove_productstockrecord_opening_stock_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productstockrecord',
            name='units_per_crate',
        ),
    ]