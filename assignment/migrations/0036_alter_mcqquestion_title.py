# Generated by Django 4.0.4 on 2022-08-17 07:02

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0035_rename_option_mcqoption'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mcqquestion',
            name='title',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
