# Generated by Django 4.2 on 2024-09-19 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process_batch', '0011_alter_batchmixingredients_ingredient_process_store'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchmixingredients',
            name='ingredient_process_store',
            field=models.IntegerField(blank=True, help_text='here it is process ingredient for base ID', null=True),
        ),
    ]