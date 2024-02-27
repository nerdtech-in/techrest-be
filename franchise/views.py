from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from rest_framework.response import Response
# Create your views here.
from rest_framework import status

class MenuAPIView(APIView):
    def get(self, request, franchise_slug, outlet_slug, table_id):
        try:
            franchise = Franchise.objects.get(slug=franchise_slug)
            outlet = Outlet.objects.get(franchise=franchise, slug=outlet_slug)
            table = Table.objects.get(id=table_id, outlet=outlet)
        except (Franchise.DoesNotExist, Outlet.DoesNotExist, Table.DoesNotExist):
            return Response({"error": "Franchise, outlet, or table not found"}, status=status.HTTP_404_NOT_FOUND)
        
        menu_items = Menu.objects.filter(franchise=franchise)
        menu_data = []
        for item in menu_items:
            menu_data.append({
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "category": item.category,
                "is_vegetarian": item.is_vegetarian
            })

        return Response({'franchise_name': franchise.name, 'menu': menu_data})
