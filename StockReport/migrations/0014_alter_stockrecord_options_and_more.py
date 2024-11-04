# Generated by Django 4.2 on 2024-10-05 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StockReport', '0013_remove_stockrecord_stock_record_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockrecord',
            options={'ordering': ['-date', '-created_at']},
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='closing_stock_lits',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='closing_stock_units',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='lit_factor',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='physical_stock',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='production_lits',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='production_units',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='sales_lits',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='sales_units',
            field=models.FloatField(default=0.0),
        ),
    ]