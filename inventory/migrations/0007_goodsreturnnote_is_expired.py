# Generated by Django 4.2 on 2024-10-16 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_remove_goodsreturnnote_is_expired'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodsreturnnote',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]
