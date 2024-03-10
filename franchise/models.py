from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from io import BytesIO
from PIL import Image
from django.conf import settings


class Franchise(models.Model):
    name = models.CharField(max_length=30, null=True)
    description = models.TextField()
    location = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    opening_hours = models.CharField(max_length=30)
    is_vegetarian = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name

class Outlet(models.Model):
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    slug = models.SlugField(unique=True, null=True)
    outlet_license = models.FileField(upload_to="outlet_license")
    photo = models.ImageField(upload_to="outlet_photo")
    code = models.CharField(max_length=20)
    no_of_employees = models.IntegerField()

    def __str__(self):
        return self.name

class Table(models.Model):
    table_number = models.IntegerField(null=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    category = models.CharField(max_length=50, choices=(("IN", "INDOOR"), ("OU", "OUTDOOR"), ("MZ", "MEZZANINE")))
    is_reserved = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes', null=True, blank=True)

    def __str__(self):
        return f"Table {self.table_number} at {self.outlet.name}"


class Category(models.Model):
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Menu(models.Model):
    sub_category  = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    # franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    icon = models.ImageField(upload_to='menu-icons')
    gif = models.FileField(upload_to='menu_gifs')
    expected_delivery = models.IntegerField(help_text="In minutes.")
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # is_vegetarian = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class MenuImage(models.Model):
    menu = models.ForeignKey(Menu,on_delete=models.CASCADE)
    image = models.ImageField(upload_to="item_image")

class Order(models.Model):
    item = models.ForeignKey(Menu,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_served = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    served_at = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.item.name
    

class KitchenOrderTicket(models.Model):
    table = models.ForeignKey(Table,on_delete=models.CASCADE,null=True)
    order = models.ManyToManyField(Order)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    served_at = models.DateTimeField(null=True)
    is_served = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            room_group_name=self.table.outlet.franchise.slug+"_"+self.table.outlet.slug
            # table_order = TableOrder.objects.get(table=self.table)
            table_orders = TableOrder.objects.filter(table=self.table)
            
            if not unserved_kots_exist:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "tables_" + room_group_name,
                    {
                        'type': 'update_table_color',
                        'table_id': self.table.id,
                        'table_color': "#48A14D",
                    }
                )
            
        except:
            pass

    def __str__(self):
        return f"Order {self.created_at}"

class Customer(models.Model):
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20)
    finger_print = models.CharField(max_length=50,null=True)
    
    def __str__(self):
        return self.name

class TableOrder(models.Model):
    table = models.ForeignKey(Table,on_delete=models.CASCADE)
    kot = models.ManyToManyField(KitchenOrderTicket)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True,null=True)
    completed_at = models.DateTimeField(null=True)
    is_paid = models.BooleanField(default=False)
    
@receiver(post_save, sender=Table)
def generate_qr_code(sender, instance, created, **kwargs):
    if created:
        qr_size = 450

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        table_id = instance.id
        outlet_slug = instance.outlet.slug
        franchise_slug = instance.outlet.franchise.slug

        qr.add_data(f'{settings.DOMAIN_NAME}/menu/{franchise_slug}/{outlet_slug}/{table_id}/')
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((qr_size, qr_size), Image.LANCZOS)  # Resize QR code image
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        instance.qr_code.save(f'qr_code_{instance.table_number}.png', buffer)

