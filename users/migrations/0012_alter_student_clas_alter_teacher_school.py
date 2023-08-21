# Generated by Django 4.0.4 on 2022-04-28 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_class_grade_level'),
        ('users', '0011_remove_teacher_clas_teacher_school'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='clas',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='core.class'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='school',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teachers', to='core.school'),
        ),
    ]
