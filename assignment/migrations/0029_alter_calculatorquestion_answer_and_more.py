# Generated by Django 4.0.4 on 2022-07-18 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0028_alter_assignmentresultdetail_sorting_question_selected_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculatorquestion',
            name='answer',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='calculatorquestion',
            name='marks',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
