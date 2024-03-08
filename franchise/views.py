from django.shortcuts import render

from .serializers import OrderSerializer
from rest_framework import viewsets
from .models import Category,Franchise,Outlet,Table,KitchenOrderTicket,TableOrder,Menu
from .serializers import CategorySerializer,FranchiseSerializer,OrderSerializer,TableOrderSerializer,KitchenOrderTicketSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import Token
from .models import Customer,Order
from django.conf import settings
import jwt
from rest_framework import status
from .authentications import IsJWTAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from . import consumer_serializers
from django.shortcuts import get_object_or_404

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    
    serializer_class = CategorySerializer


class CustomerAPIView(APIView):
    def post(self,request):
        try:
            customer = Customer.objects.get(mobile_number=request.data['mobile_number'])
        except:
            customer = Customer.objects.create(name=request.data['name'], mobile_number=request.data['mobile_number'])
        
        access_token = jwt.encode({
                "id":customer.id,
                "name":customer.name,
                "mobile_number":customer.mobile_number
            },settings.SECRET_KEY,algorithm="HS256")
        return Response({"access_token":access_token})


class TableAPIView(APIView):
    authentication_classes = [IsJWTAuthenticated]
    def get(self, request, franchise_slug, outlet_slug, table_id):
        try:
            table = Table.objects.get(id=table_id)
            franchise = Franchise.objects.get(slug=franchise_slug)
            outlet = Outlet.objects.get(slug=outlet_slug, franchise=franchise)
        except (Table.DoesNotExist, Franchise.DoesNotExist, Outlet.DoesNotExist):
            return Response({'msg':'invalid url'})

        serializer = FranchiseSerializer(franchise)
        new_data = serializer.data
        new_data['table_id'] = table_id
        return Response(new_data)
    

class OrderAPIView(APIView):
    authentication_classes = [IsJWTAuthenticated]
    def post(self, request):
        order_dict = dict()
        customer = request.user
        serializer = OrderSerializer(data=request.data['products'], many=True)
        if serializer.is_valid():
            orders = serializer.save()
            order_dict=serializer.data
            kot = KitchenOrderTicket.objects.create()
            kot.order.add(*orders)
            table_id = request.data.get('table_id')
            table=Table.objects.get(id=table_id)
            table_order, created = TableOrder.objects.get_or_create(
                table_id=table_id,
                customer_id=customer.id
            )
            table_order.kot.add(kot)
            room_group_name = table.outlet.franchise.slug+"_"+table.outlet.slug
            send_order_to_consumers(room_group_name,order_dict)
            serializer = consumer_serializers.TableOrderSerializer(table_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_order_to_consumers(room_group_name,table_order):
    channel_layer = get_channel_layer()
    
    orders_with_names = []
    for order in table_order:
        item_id = order['item']
        quantity = order['quantity']
        item = get_object_or_404(Menu, id=item_id)
        orders_with_names.append({
            'item_name': item.name,
            'quantity': quantity
        })
        
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'order_details',
            'order': json.dumps(orders_with_names),
        }
    )
    # print(serializer.data)

def orders_view(request, franchise, outlet):
    # Pass franchise and outlet data to the template
    context = {
        'franchise': franchise,
        'outlet': outlet
    }
    return render(request, 'outlet_tables.html', context)
