# Generated by Django 4.2 on 2024-09-19 07:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('process_store', '0001_initial'),
        ('process_batch', '0010_alter_batchmix_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchmixingredients',
            name='ingredient_process_store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ingredient_base_process_store', to='process_store.processstore'),
        ),
    ]
