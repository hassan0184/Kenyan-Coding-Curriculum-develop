# Generated by Django 4.0.4 on 2022-04-23 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_teacher_otp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='otp',
        ),
        migrations.AddField(
            model_name='teacher',
            name='secret_key',
            field=models.CharField(default='NKAUZXWETZ3ADULIDBU7NFN5GL4NM2FJ', max_length=32),
        ),
    ]
