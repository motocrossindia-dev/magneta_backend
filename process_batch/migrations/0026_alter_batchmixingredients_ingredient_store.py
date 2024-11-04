# Generated by Django 4.2 on 2024-10-16 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_store_typename'),
        ('process_batch', '0025_batchmixingredients_ingredient_store'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchmixingredients',
            name='ingredient_store',
            field=models.ManyToManyField(blank=True, null=True, related_name='batch_mix_ingredients', to='inventory.store'),
        ),
    ]
