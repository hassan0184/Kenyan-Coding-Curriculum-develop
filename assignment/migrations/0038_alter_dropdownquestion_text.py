# Generated by Django 4.0.4 on 2022-08-17 10:51

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0037_mcqquestion_max_select_alter_mcqoption_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dropdownquestion',
            name='text',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
