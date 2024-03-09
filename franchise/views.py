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

def orders_view(request, franchise, outlet):
    context = {
        'franchise': franchise,
        'outlet': outlet
    }
    return render(request, 'outlet_tables.html', context)

def table_view(request, franchise, outlet):
    blue = "#2c6fbb"
    grey = "#c7c5c5"
    red = "red"
    green = "#48A14D"

    outlet = Outlet.objects.get(slug=outlet)
    tables = Table.objects.filter(outlet=outlet)
    
    # Create separate dictionaries for each category
    indoor_tables = []
    outdoor_tables = []
    mezzanine_tables = []

    for table in tables:
        color = green  # Default color is green

        # Check if the table is not reserved
        if not table.is_reserved:
            color = grey
        else:
            try:
                # Check if there is a TableOrder associated with this table
                table_order = TableOrder.objects.get(table=table)
            except TableOrder.DoesNotExist:
                color = blue  # If no TableOrder, set color to blue
            else:
                # If there is a TableOrder, check if all KOTs associated with it are served
                if not table_order.kot.filter(is_served=False).exists():
                    color = green  # If all KOTs are served, set color to green
                else:
                    color = red  # If any KOT is not served, set color to red

        # Append table details along with its color to the respective category dictionary
        if table.category == "IN":
            indoor_tables.append({
                "table_id": table.table_number,
                "table_color": color,
                "table_type": table.category
            })
        elif table.category == "OU":
            outdoor_tables.append({
                "table_id": table.table_number,
                "table_color": color,
                "table_type": table.category
            })
        elif table.category == "MZ":
            mezzanine_tables.append({
                "table_id": table.table_number,
                "table_color": color,
                "table_type": table.category
            })

    context = {
        "tables":[indoor_tables,outdoor_tables,mezzanine_tables]
    }
    return render(request, template_name="order_per_table.html", context=context)

