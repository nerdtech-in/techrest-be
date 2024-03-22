from django.contrib import admin
from .models import Franchise, Outlet, Table, Category, SubCategory, Menu, MenuImage, Order, KitchenOrderTicket, Customer, TableOrder


def generate_qr_codes(modeladmin, request, queryset):
    for table in queryset:
        table.generate_qr_code()
    modeladmin.message_user(request, "QR codes generated successfully.")

generate_qr_codes.short_description = "Generate QR codes"

class MenuImageInline(admin.TabularInline):
    model = MenuImage
    extra = 1

class MenuInline(admin.TabularInline):
    model = Menu
    extra = 1

class TableOrderInline(admin.TabularInline):
    model = TableOrder
    extra = 1

class TableInline(admin.TabularInline):
    model = Table
    extra = 1

class OrderInline(admin.TabularInline):
    model = Order
    extra = 1

class KitchenOrderTicketInline(admin.TabularInline):
    model = KitchenOrderTicket
    extra = 1

class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1

class OutletInline(admin.TabularInline):
    model = Outlet
    extra = 1

@admin.register(Franchise)
class FranchiseAdmin(admin.ModelAdmin):
    inlines = [OutletInline]

@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    inlines = [TableInline]

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    inlines = [TableOrderInline]
    actions = [generate_qr_codes,]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryInline]

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['id','name','price','sub_category']
    inlines = [MenuImageInline]

@admin.register(TableOrder)
class TableOrderAdmin(admin.ModelAdmin):
    # inlines = [OrderInline]
    pass

@admin.register(KitchenOrderTicket)
class KitchenOrderTicketAdmin(admin.ModelAdmin):
    pass

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    inlines = [MenuInline,]