from django.db import models
from django.contrib.auth.models import User

class Franchise(models.Model):
    name = models.CharField(max_length=30,null=True)
    description = models.TextField()
    location = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    opening_hours = models.CharField(max_length=30)
    is_vegiterian = models.BooleanField(default=True)
    slug = models.SlugField(unique=True,null=True)
    
    def __str__(self):
        return self.name

class Outlet(models.Model):
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    slug = models.SlugField(unique=True,null=True)
    outlet_license = models.FileField(upload_to="outlet_license")
    photo = models.ImageField(upload_to= "outlet_photo")
    code = models.CharField(max_length=20)
    no_of_employees = models.IntegerField()

    def __str__(self):
        return self.name

class Table(models.Model):
    table_number = models.IntegerField(null=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    category = models.CharField(max_length=50,choices=(("IN","INDOOR"),("OU","OUTDOOR"),('MZ','MEZZANINE')))
    is_reserved = models.BooleanField(default=False)
    
class Menu(models.Model):
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=50)
    is_vegetarian = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    # Add any other fields relevant to your order

    def __str__(self):
        return f"Order {self.item.name} at Table {self.table.table_number} - {self.created_at}"