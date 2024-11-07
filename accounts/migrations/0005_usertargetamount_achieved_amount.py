# Generated by Django 5.1.2 on 2024-11-07 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_usertargetamount_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertargetamount',
            name='achieved_amount',
            field=models.FloatField(default=0.0, help_text='Total amount achieved by user'),
        ),
    ]