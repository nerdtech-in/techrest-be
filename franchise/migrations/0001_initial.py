# Generated by Django 5.0.2 on 2024-02-25 05:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Franchise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, null=True)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=100)),
                ('opening_hours', models.CharField(max_length=30)),
                ('is_vegiterian', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('category', models.CharField(max_length=50)),
                ('is_vegetarian', models.BooleanField(default=False)),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='franchise.franchise')),
            ],
        ),
        migrations.CreateModel(
            name='Outlet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=20)),
                ('outlet_license', models.FileField(upload_to='outlet_license')),
                ('photo', models.ImageField(upload_to='outlet_photo')),
                ('code', models.CharField(max_length=20)),
                ('no_of_employees', models.IntegerField()),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='franchise.franchise')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_number', models.IntegerField(null=True)),
                ('status', models.BooleanField(default=True)),
                ('capacity', models.IntegerField()),
                ('category', models.CharField(choices=[('INDOOR', 'INDOOR'), ('OUTDOOR', 'OUTDOOR')], max_length=50)),
                ('is_reserved', models.BooleanField(default=False)),
                ('outlet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='franchise.outlet')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='franchise.menu')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='franchise.table')),
            ],
        ),
    ]
