# Generated by Django 5.0.2 on 2024-03-13 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('franchise', '0007_kitchenorderticket_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='tableorder',
            name='is_pending',
            field=models.BooleanField(default=False),
        ),
    ]