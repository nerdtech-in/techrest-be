from django.db import models

# Create your models here.

class Franchise(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
    
class Outlet(models.Model):
    franchise = models.ForeignKey(Franchise,on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class Table(models.Model):
    table_number = models.IntegerField(null=True)
    table_name = models.CharField(max_length=30,null=True)
    outlet = models.ForeignKey(Outlet,on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    
class Menu(models.Model):
    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    franchise = models.ForeignKey(Franchise,on_delete=models.CASCADE)