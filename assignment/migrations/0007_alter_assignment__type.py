# Generated by Django 4.0.4 on 2022-06-08 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0006_alter_assignmentresult_marks_obtained_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='_type',
            field=models.CharField(choices=[('1', 'Assesment by TEKS'), ('2', 'Assesment by Skills'), ('3', 'Assesment by Work sheet')], default='1', max_length=30),
        ),
    ]
