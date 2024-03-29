# Generated by Django 5.0.2 on 2024-03-10 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('franchise', '0005_customer_finger_print'),
    ]

    operations = [
        migrations.AddField(
            model_name='kitchenorderticket',
            name='served_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='is_served',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='served_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='tableorder',
            name='completed_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='tableorder',
            name='started_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='kitchenorderticket',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
