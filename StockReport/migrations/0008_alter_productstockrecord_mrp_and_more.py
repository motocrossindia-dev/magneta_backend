# Generated by Django 4.2 on 2024-10-03 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        ('StockReport', '0007_remove_productstockrecord_units_per_crate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productstockrecord',
            name='mrp',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='opening_stock_lits',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='opening_stock_units',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='productstockrecord',
            name='volume_nos',
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name='OpeningStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opening_stock', models.IntegerField(default=0)),
                ('closing_stock', models.IntegerField(default=0)),
                ('physical_stock', models.IntegerField(default=0)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='opening_stock', to='products.product')),
            ],
        ),
    ]