# Generated by Django 4.0.4 on 2022-08-17 13:52

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0040_remove_fillinblankquestion_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='FractionModel1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField()),
                ('total_boxes', models.IntegerField()),
                ('marks', models.IntegerField(null=True)),
                ('correct_number', models.IntegerField()),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assignment.assignment')),
            ],
        ),
    ]
