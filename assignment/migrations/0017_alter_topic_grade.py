# Generated by Django 4.0.4 on 2022-07-07 13:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_class_grade_level'),
        ('assignment', '0016_alter_fillinblankquestion_assignment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.grade'),
        ),
    ]
