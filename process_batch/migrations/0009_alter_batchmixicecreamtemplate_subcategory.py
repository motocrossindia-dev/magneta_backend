# Generated by Django 4.2 on 2024-09-14 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('process_batch', '0008_batchmixicecreamtemplate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchmixicecreamtemplate',
            name='subCategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batchMixIceCreamSubCategory', to='process_batch.batchmixsubcategory'),
        ),
    ]