# Generated by Django 4.0.4 on 2022-11-30 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_school_is_approved_school_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestedSchool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('type', models.CharField(max_length=255)),
                ('district', models.CharField(max_length=255)),
                ('is_approved', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Requested Schools',
            },
        ),
        migrations.AlterModelOptions(
            name='school',
            options={'verbose_name_plural': 'Approved Schools'},
        ),
        migrations.RemoveField(
            model_name='school',
            name='is_approved',
        ),
    ]
