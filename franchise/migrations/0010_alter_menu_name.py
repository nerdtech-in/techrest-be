# Generated by Django 5.0.2 on 2024-03-18 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('franchise', '0009_alter_menu_gif_alter_menu_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]