# Generated by Django 4.0.4 on 2022-06-16 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_class_school_alter_class_teacher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('name', 'grade_level')},
        ),
    ]
