# Generated by Django 4.2 on 2024-10-03 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributors', '0002_retailerorders_discount_percentage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='retailerorders',
            name='discount_percentage',
        ),
        migrations.AddField(
            model_name='retailermainorders',
            name='discount_percentage',
            field=models.FloatField(default=0.0),
        ),
    ]
