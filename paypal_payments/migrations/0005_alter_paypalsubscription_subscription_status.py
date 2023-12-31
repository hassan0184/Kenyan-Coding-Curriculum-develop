# Generated by Django 4.0.4 on 2022-07-07 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paypal_payments', '0004_rename_paypalcustomersubscription_paypalcustomer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paypalsubscription',
            name='subscription_status',
            field=models.CharField(choices=[('Active', 'Active'), ('Canceled', 'Canceled'), ('Expired', 'Expired'), ('PastDue', 'Past Due'), ('Pending', 'Pending')], max_length=100, null=True),
        ),
    ]
