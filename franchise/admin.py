from django.contrib import admin
from .models import *
from nested_admin import NestedTabularInline, NestedModelAdmin
# Register your models here.

## Inline
class MenuInline(NestedTabularInline):
    model = Menu
    extra = 1

class TableInline(NestedTabularInline):
    model = Table
    extra = 1

class OutletInline(NestedTabularInline):
    model = Outlet
    extra = 1
    inlines = [TableInline]
    min_num = 1

# admin

class OutletAdmin(NestedModelAdmin):
    inlines = [TableInline,]
    list_display = ['id','name','franchise']

class FranchiseAdmin(NestedModelAdmin):
    inlines = [OutletInline,MenuInline]


admin.site.register(Franchise,FranchiseAdmin)
admin.site.register(Outlet,OutletAdmin)
admin.site.register(Table)
admin.site.register(Menu)