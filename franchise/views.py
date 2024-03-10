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

class CustomerFingerAPIView(APIView):
    def post(self,request):
        try:
            customer = Customer.objects.get(finger_print=request.data["finger_print"])
        except:
            return Response({'msg':'Invalid Finger Print'})
        
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
            kot.table=table
            kot.save()
            table.is_reserved=True
            table.save()
            table_order, created = TableOrder.objects.get_or_create(
                table_id=table_id,
                customer_id=customer.id
            )
            table_order.kot.add(kot)
            room_group_name = table.outlet.franchise.slug+"_"+table.outlet.slug
            send_order_to_consumers(room_group_name,order_dict,table_id)
            serializer = consumer_serializers.TableOrderSerializer(table_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_order_to_consumers(room_group_name,table_order,table_id):
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
    async_to_sync(channel_layer.group_send)(
        "tables_"+room_group_name,
        {
            'type': 'update_table_color',
            'table_id': table_id,
            'table_color': "#B33F40",
        }
    )

def orders_view(request, franchise, outlet):
    context = {
        'franchise': franchise,
        'outlet': outlet
    }
    return render(request, 'outlet_tables.html', context)

def table_view(request, franchise, outlet):
    blue = "#2c6fbb"
    grey = "#c7c5c5"
    red = "#B33F40"
    green = "#48A14D"

    new = Outlet.objects.get(slug=outlet)
    tables = Table.objects.filter(outlet=new)
    indoor_tables = []
    outdoor_tables = []
    mezzanine_tables = []

    for table in tables:
        color = green
        if not table.is_reserved:
            color = grey
        else:
            try:
                table_order = TableOrder.objects.get(table=table)
            except TableOrder.DoesNotExist:
                color = blue
            else:
                if not table_order.kot.filter(is_served=False).exists():
                    color = green
                else:
                    color = red 
                if table_order.is_paid:
                    color = grey
                    
        if table.category == "IN":
            indoor_tables.append({
                "table_id": table.table_number,
                "id": table.id,
                "table_color": color,
                "table_type": "Indoor"
            })
        elif table.category == "OU":
            outdoor_tables.append({
                "table_id": table.table_number,
                "id": table.id,
                "table_color": color,
                "table_type": "Outdoor"
            })
        elif table.category == "MZ":
            mezzanine_tables.append({
                "table_id": table.table_number,
                "id": table.id,
                "table_color": color,
                "table_type": "Mezzanine"
            })

    context = {
        "tables":[indoor_tables,outdoor_tables,mezzanine_tables],
        "franchise":franchise, "outlet": outlet,
    }
    return render(request, template_name="order_per_table.html", context=context)

def show_table_order(request,franchise, outlet,table_id):
    try:
        table_order = TableOrder.objects.filter(table_id=table_id, is_paid=False).first()
        if table_order:
            kots = table_order.kot.all()
            orders = []
            for kot in kots:
                order_details = []
                for order in kot.order.all():
                    order_details.append({
                        'item_name': order.item.name,
                        'quantity': order.quantity
                    })
                orders.append({
                    'kot_id': kot.id,
                    'order_details': order_details
                })
            return render(request, 'table_order.html', {'table_order': table_order, 'orders': orders})
        else:
            return render(request, 'table_order.html', {'error': 'Table order not found or already paid.'})
    except Exception as e:
        return render(request, 'table_order.html', {'error': str(e)})
