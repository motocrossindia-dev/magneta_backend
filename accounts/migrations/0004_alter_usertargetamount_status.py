# Generated by Django 5.1.2 on 2024-11-06 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_usertargetamount_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertargetamount',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=10),
        ),
    ]