# Generated by Django 4.0.4 on 2022-08-17 09:05

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0036_alter_mcqquestion_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='mcqquestion',
            name='max_select',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='mcqoption',
            name='text',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='mcqquestion',
            name='marks',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
