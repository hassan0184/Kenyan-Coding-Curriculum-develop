# Generated by Django 4.0.4 on 2022-07-12 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0018_calculatorquestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculatorquestion',
            name='assignment',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='calculator_questions', to='assignment.assignment'),
            preserve_default=False,
        ),
    ]
