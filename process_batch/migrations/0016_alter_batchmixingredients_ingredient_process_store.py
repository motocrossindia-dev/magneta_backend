# Generated by Django 4.2 on 2024-09-19 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process_store', '0001_initial'),
        ('process_batch', '0015_alter_batchmixingredients_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchmixingredients',
            name='ingredient_process_store',
            field=models.ManyToManyField(to='process_store.processstore'),
        ),
    ]
