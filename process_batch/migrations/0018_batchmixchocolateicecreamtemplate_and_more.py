# Generated by Django 4.2 on 2024-09-23 04:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('process_batch', '0017_alter_batchmixingredients_ingredient_process_store'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchMixChocolateIceCreamTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batchName', models.CharField(max_length=100)),
                ('batchCode', models.CharField(max_length=100)),
                ('expDays', models.CharField(max_length=10)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('subCategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='process_batch.batchmixsubcategory')),
            ],
            options={
                'verbose_name_plural': 'BatchMixChocolateIceCreamTemplate',
            },
        ),
        migrations.CreateModel(
            name='BatchMixkulfyTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batchName', models.CharField(max_length=100)),
                ('batchCode', models.CharField(max_length=100)),
                ('expDays', models.CharField(max_length=10)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('subCategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='process_batch.batchmixsubcategory')),
            ],
            options={
                'verbose_name_plural': 'BatchMixkulfyTemplate',
            },
        ),
        migrations.CreateModel(
            name='BatchMixkulfyTemplateIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('type', models.CharField(choices=[('RMStore', 'RMStore'), ('ProcessStore', 'ProcessStore')], default='RMStore', max_length=20)),
                ('lowerLimit', models.FloatField(max_length=20)),
                ('percentage', models.FloatField(max_length=20)),
                ('upperLimit', models.FloatField(max_length=20)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='process_batch.batchmixkulfytemplate')),
            ],
            options={
                'verbose_name_plural': 'BatchMixkulfyTemplateIngredients',
            },
        ),
        migrations.CreateModel(
            name='BatchMixChocolateIceCreamTemplateIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('type', models.CharField(choices=[('RMStore', 'RMStore'), ('ProcessStore', 'ProcessStore')], default='RMStore', max_length=20)),
                ('lowerLimit', models.FloatField(max_length=20)),
                ('percentage', models.FloatField(max_length=20)),
                ('upperLimit', models.FloatField(max_length=20)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='process_batch.batchmixchocolateicecreamtemplate')),
            ],
            options={
                'verbose_name_plural': 'BatchMixChocolateIceCreamTemplateIngredients',
            },
        ),
    ]