# Generated by Django 4.0.4 on 2022-05-25 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0005_alter_class_school_alter_class_teacher'),
        ('users', '0017_student_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('_type', models.CharField(choices=[('1', 'Assesment by TEKS'), ('2', 'Assesment by Skills')], default='1', max_length=30)),
                ('is_pre_test', models.BooleanField(default=False)),
                ('is_post_test', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('marks', models.DecimalField(decimal_places=2, max_digits=5)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='assignment.assignment')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('grade', models.CharField(choices=[('1', 'First'), ('2', 'Second'), ('3', 'Third'), ('4', 'Fourth'), ('5', 'Fifth'), ('6', 'Sixth'), ('7', 'Seventh'), ('8', 'Eight'), ('9', 'Ninth'), ('10', 'Tenth'), ('11', 'Eleventh')], default='1', max_length=20)),
            ],
            options={
                'unique_together': {('name', 'grade')},
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='assignment.question')),
                ('selected_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='assignment.option')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='users.student')),
            ],
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='assignment.question'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='assignment.topic'),
        ),
        migrations.CreateModel(
            name='AssignedAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateTimeField()),
                ('to_date', models.DateTimeField()),
                ('_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_assignments', to='core.class')),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_assignments', to='assignment.assignment')),
                ('students', models.ManyToManyField(to='users.student')),
            ],
        ),
    ]
