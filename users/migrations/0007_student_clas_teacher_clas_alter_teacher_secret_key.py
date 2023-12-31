# Generated by Django 4.0.4 on 2022-04-25 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('users', '0006_alter_teacher_secret_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='clas',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='core.class'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='clas',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teachers', to='core.class'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='secret_key',
            field=models.CharField(default='KWOPCWOJTJ75GHPYW6IZNNKAZ7UDMHZ2', max_length=32),
        ),
    ]
