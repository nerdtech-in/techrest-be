# Generated by Django 5.0.2 on 2024-03-09 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('franchise', '0004_remove_customer_finger_print'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='finger_print',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
