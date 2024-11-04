# Generated by Django 4.2.15 on 2024-08-29 06:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchMix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batchName', models.CharField(max_length=100)),
                ('batchCode', models.CharField(max_length=100)),
                ('batchDate', models.DateField()),
                ('expDate', models.DateField(blank=True, null=True)),
                ('totalVolume', models.FloatField(max_length=20)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'SyrupBatchMix',
            },
        ),
        migrations.CreateModel(
            name='BatchMixCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'BatchMixCategory',
            },
        ),
        migrations.CreateModel(
            name='BatchMixSubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='process_batch.batchmixcategory')),
            ],
            options={
                'verbose_name_plural': 'BatchMixSubCategory',
            },
        ),
        migrations.CreateModel(
            name='BatchMixTemplate',
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
                'verbose_name_plural': 'BatchMixTemplateSyrupAndSauce',
            },
        ),
        migrations.CreateModel(
            name='BatchMixTemplateIngredients',
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
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='process_batch.batchmixtemplate')),
            ],
            options={
                'verbose_name_plural': 'BatchMixTemplateIngredientsSyrupAndSauce',
            },
        ),
        migrations.CreateModel(
            name='BatchMixIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.FloatField(max_length=20)),
                ('quantity', models.FloatField(max_length=20)),
                ('grnlist', models.JSONField(default=list)),
                ('rate', models.FloatField(default=0.0, max_length=20)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('SyrupBatchMix', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='process_batch.batchmix')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.material')),
            ],
            options={
                'verbose_name_plural': 'SyrupBatchMixIngredients',
            },
        ),
        migrations.AddField(
            model_name='batchmix',
            name='subCategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='process_batch.batchmixsubcategory'),
        ),
    ]