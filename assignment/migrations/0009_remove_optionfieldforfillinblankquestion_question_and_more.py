# Generated by Django 4.0.4 on 2022-06-27 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0008_fillinblankquestion_textfieldforfillinblankquestion_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='optionfieldforfillinblankquestion',
            name='question',
        ),
        migrations.RemoveField(
            model_name='optionfieldforfillinblankquestion',
            name='sorting_number',
        ),
        migrations.AddField(
            model_name='textfieldforfillinblankquestion',
            name='options',
            field=models.ManyToManyField(related_name='options', to='assignment.optionfieldforfillinblankquestion'),
        ),
    ]
