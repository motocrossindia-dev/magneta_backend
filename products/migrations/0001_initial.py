# Generated by Django 4.2.15 on 2024-08-29 06:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('price', models.FloatField(max_length=10)),
                ('carton_size', models.IntegerField()),
                ('product_barcode', models.IntegerField(default=0)),
                ('carton_barcode', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('gst', models.FloatField(default=0.0, max_length=5)),
                ('factory_gst', models.FloatField(default=0.0, max_length=10)),
                ('factory_sale', models.FloatField(default=0.0, max_length=10)),
                ('distributor_margin_rate', models.FloatField(default=0.0, max_length=5)),
                ('distributor_margin_price', models.FloatField(default=0.0, max_length=10)),
                ('distributor_gst', models.FloatField(default=0.0, max_length=10)),
                ('distributor_sale', models.FloatField(default=0.0, max_length=10)),
                ('retailer_margin_rate', models.FloatField(default=0.0, max_length=5)),
                ('retailer_margin_price', models.FloatField(default=0.0, max_length=10)),
                ('retailer_gst', models.FloatField(default=0.0, max_length=10)),
                ('retailer_sale', models.FloatField(default=0.0, max_length=10)),
                ('retailer_base_price', models.FloatField(default=0.0, max_length=10)),
                ('retailer_base_gst', models.FloatField(default=0.0, max_length=10)),
                ('mrp', models.FloatField(default=0.0, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductSpecification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specification_name', models.CharField(max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_specifications', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size_name', models.CharField(max_length=100)),
                ('size_volume', models.CharField(max_length=50)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_sizes', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_images', models.ImageField(upload_to='product_images/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_images', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductFlavour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flavour_name', models.CharField(max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_flavours', to='products.product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.subcategory'),
        ),
    ]