# Generated by Django 4.0.4 on 2022-04-28 06:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_class_teacher'),
        ('users', '0010_alter_teacher_secret_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='clas',
        ),
        migrations.AddField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teachers', to='core.school'),
        ),
    ]
