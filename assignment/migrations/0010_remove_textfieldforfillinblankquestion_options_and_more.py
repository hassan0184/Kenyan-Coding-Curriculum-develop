# Generated by Django 4.0.4 on 2022-06-27 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0009_remove_optionfieldforfillinblankquestion_question_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textfieldforfillinblankquestion',
            name='options',
        ),
        migrations.AddField(
            model_name='optionfieldforfillinblankquestion',
            name='question',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='assignment.textfieldforfillinblankquestion'),
            preserve_default=False,
        ),
    ]