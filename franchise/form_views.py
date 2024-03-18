from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import OrderForm
from .models import SubCategory
from django.shortcuts import render


from django.shortcuts import render
from .models import Category

def create_order(request,table_id,user_id):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'create_order.html', context)


def order_success(request):
    return render(request, 'order_success.html')
