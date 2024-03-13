from rest_framework import serializers
from .models import *

class MenuImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuImage
        fields = ('image',)

class MenuSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    class Meta:
        model = Menu
        fields = ('id','name', 'icon', 'gif', 'expected_delivery', 'description', 'price', 'images')
        
    def get_images(self,obj):
        return MenuImageSerializer(MenuImage.objects.filter(menu=obj),many=True).data

class SubCategorySerializer(serializers.ModelSerializer):
    menus = serializers.SerializerMethodField()

    class Meta:
        model = SubCategory
        fields = ('name', 'menus')
        
    def get_menus(self,obj):
        menu = Menu.objects.filter(sub_category_id=obj)
        return MenuSerializer(menu, many=True).data

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('name', 'subcategories')
    
    def get_subcategories(self,obj):
        subcategories = SubCategory.objects.filter(category=obj)
        return SubCategorySerializer(subcategories, many=True).data
    
class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = '__all__'
        
class FranchiseSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    outlet = serializers.SerializerMethodField()
    
    class Meta:
        model = Franchise
        fields = '__all__'
    
    def get_categories(self,obj):
        categories = Category.objects.filter(franchise=obj)
        return CategorySerializer(categories, many=True).data
    
    def get_outlet(self,obj):
        outlet = Outlet.objects.get(franchise=obj)
        return OutletSerializer(outlet).data

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class KitchenOrderTicketSerializer(serializers.ModelSerializer):
    order = OrderSerializer(many=True)
    class Meta:
        model = KitchenOrderTicket
        fields = '__all__'

class TableOrderSerializer(serializers.ModelSerializer):
    kot = KitchenOrderTicketSerializer(many=True, read_only=True)

    class Meta:
        model = TableOrder
        fields = '__all__'
