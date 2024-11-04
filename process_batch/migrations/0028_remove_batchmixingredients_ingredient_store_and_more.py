# Generated by Django 4.2 on 2024-10-16 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process_store', '0001_initial'),
        ('process_batch', '0027_remove_batchmixingredients_ingredient_process_store_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batchmixingredients',
            name='ingredient_store',
        ),
        migrations.RemoveField(
            model_name='batchmixingredients',
            name='ingredient_process_store',
        ),
        migrations.AddField(
            model_name='batchmixingredients',
            name='ingredient_process_store',
            field=models.ManyToManyField(related_name='batch_mix_ingredient_process', to='process_store.processstore'),
        ),
    ]
