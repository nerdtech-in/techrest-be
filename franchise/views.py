from datetime import datetime
from django.shortcuts import render
from django.db.models import F
from .serializers import OrderSerializer
from rest_framework import viewsets
from .models import Category,Franchise,Outlet,Table,KitchenOrderTicket,TableOrder,Menu
from .serializers import CategorySerializer,FranchiseSerializer,OrderSerializer,TableOrderSerializer,KitchenOrderTicketSerializer,UserTableOrderSerializer,PaymentSerializer
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
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


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
    
class MenuAPIView(APIView):
    def get(self, request, franchise_slug, outlet_slug):
        try:
            # table = Table.objects.get(id=table_id)
            franchise = Franchise.objects.get(slug=franchise_slug)
            outlet = Outlet.objects.get(slug=outlet_slug, franchise=franchise)
        except (Franchise.DoesNotExist, Outlet.DoesNotExist):
            return Response({'msg':'invalid url'})
        
        serializer = FranchiseSerializer(franchise)
        new_data = serializer.data
        # new_data['table_id'] = table_id
        return Response(new_data)
    
class OrderAPIView(APIView):
    authentication_classes = [IsJWTAuthenticated]
    def post(self, request):
        table_id = request.data.get('table_id')
        table=Table.objects.get(id=table_id)
        customer = request.user
        # if table.is_reserved:
        #     try:
        #         table_order = TableOrder.objects.get(table=table,customer=customer,is_paid=False)
        #     except:
        #         return Response({'msg':'Table is Already Reserved'})
        order_dict = dict()
        serializer = OrderSerializer(data=request.data['products'], many=True)
        if serializer.is_valid():
            orders = serializer.save()
            order_dict=serializer.data
            kot = KitchenOrderTicket.objects.create()
            kot.order.add(*orders)
            kot.table=table
            kot.save()
            table.is_reserved=True
            table.save()
            try:
                table_order = TableOrder.objects.get(table=table,customer=customer,is_paid=False)
                if table_order is None:
                    table_order = TableOrder.objects.create(table=table, customer=customer)
                
            except TableOrder.DoesNotExist:
                table_order = TableOrder.objects.create(table=table, customer=customer)
            table_order.kot.add(kot)
            room_group_name = table.outlet.franchise.slug+"_"+table.outlet.slug
            table_code = table.category+str(table.table_number)
            send_order_to_consumers(room_group_name,order_dict,table_id,table.table_number,table_code)
            serializer = consumer_serializers.TableOrderSerializer(table_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_order_to_consumers(room_group_name,table_order,table_id,table_number,table_code):
    channel_layer = get_channel_layer()
    
    orders_with_names = []
    for order in table_order:
        item_id = order['item']
        quantity = order['quantity']
        item = get_object_or_404(Menu, id=item_id)
        orders_with_names.append({
            'item_name': item.name,
            'quantity': quantity,
            'table_number':table_number,
            'table_id': table_id,
            'order_id':order['id'],
            'table_code':table_code
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
    
    unpaid_table_orders = TableOrder.objects.filter(table__in=tables, is_paid=False)

    unpaid_kots = KitchenOrderTicket.objects.filter(table__in=tables, tableorder__in=unpaid_table_orders, is_served=False)

    unserved_orders = Order.objects.filter(
        kitchenorderticket__in=unpaid_kots, is_served=False
        ).annotate(table_number=F('kitchenorderticket__table__table_number'))
    
    
    for table in tables:
        color = blue
        if not table.is_reserved:
            color = grey
        else:
            try:
                table_order = TableOrder.objects.get(table=table,is_paid=False)
            except TableOrder.DoesNotExist:
                color = blue
            else:
                if not table_order.kot.filter(is_served=False).exists():
                    color = blue
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
        "tables":[outdoor_tables,indoor_tables,mezzanine_tables],
        "franchise":franchise, "outlet": outlet,
        "orders":unserved_orders,
    }
    return render(request, template_name="order_per_table.html", context=context)

def show_table_order(request,franchise, outlet,table_id):
    try:
        total = 0
        table_order = TableOrder.objects.filter(table_id=table_id, is_paid=False).first()
        if table_order:
            kots = table_order.kot.all()
            orders = []
            for kot in kots:
                order_details = []
                for order in kot.order.all():
                    order_details.append({
                        'item_name': order.item.name,
                        'quantity': order.quantity,
                        'price':order.item.price*order.quantity
                    })
                    total+=order.item.price*order.quantity
                orders.append({
                    'kot_id': kot.id,
                    'order_details': order_details,
                })
                
            return render(request, 'table_order.html', {'table_order': table_order, 'orders': orders,'total':total})
        else:
            return render(request, 'table_order.html', {'error': 'Table order not found or already paid.'})
    except Exception as e:
        return render(request, 'table_order.html', {'error': str(e)})


class MarkOrderServedView(APIView):
    def post(self, request):
        try:
            order_id = request.data.get('orderId')
            order = Order.objects.get(pk=order_id)
            order.served_at = datetime.now()
            order.is_served = True
            order.save()
            kot = KitchenOrderTicket.objects.filter(order=order).first()
            total_orders = kot.order.count()
            served_orders = kot.order.filter(is_served=True).count()
            
            if served_orders==total_orders:
                kot.is_served=True
                kot.served_at = datetime.now()
                kot.save()
            
            return Response({'message': f'Order {order_id} marked as served'})
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)
        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=500)
        
class TableOrderAPIView(APIView):
    authentication_classes = [IsJWTAuthenticated]
    def get(self,request):
        customer = request.user
        table_orders = TableOrder.objects.filter(customer=customer,is_paid=False)
        serializer = UserTableOrderSerializer(table_orders,many=True)
        return Response(serializer.data)
    
    
class PaymentAPIView(APIView):
    authentication_classes = [IsJWTAuthenticated]
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            table_order_id = serializer.validated_data['table_order_id']
            payment_method = serializer.validated_data['payment_method']
            try:
                table_order = TableOrder.objects.get(pk=table_order_id)
                if table_order.is_paid:
                    return Response({'msg':'Order is Already Paid'})
                else:
                    table_order.is_paid = True
                table_order.payment_method = payment_method
                table_order.save()
                table = Table.objects.get(id=table_order.table.id)
                table.is_reserved = False
                table.save()
                return Response({"msg": "Payment successful."}, status=status.HTTP_200_OK)
            except TableOrder.DoesNotExist:
                return Response({"msg": "Table order not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class MakePaymentAPIView(APIView):
    def post(self, request):
        payment_method = request.data.get('paymentMethod')
        table_order_id = request.data.get('table_order_id')
        print(payment_method,table_order_id)
        table_order = TableOrder.objects.get(id=table_order_id)
        table_order.is_paid=True
        table_order.payment_method=payment_method.title()
        table = Table.objects.get(id=table_order.table.id)
        table.is_reserved=False
        table.save()
        table_order.save()
        if payment_method == 'cash':
            return Response({'msg': 'Cash payment processed successfully.'}, status=status.HTTP_200_OK)
        elif payment_method == 'online':
            return Response({'msg': 'Online payment processed successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid payment method.'}, status=status.HTTP_400_BAD_REQUEST)

class QRAPIView(APIView):
    def post(self,request):
        tables = Table.objects.all()
        link = request.data['link']
        for table in tables:
            table.generate_qr_code(link)
        return Response({'msg':"QR Changed"})
    
class MakePaymentAPIView(APIView):
    def post(self,request):
        try:
            table_order = TableOrder.objects.get(id=request.data['table_order_id'])
            table_order.is_ready_pay = True
            table_order.is_paid = True
            table_order.save()
            table = Table.objects.get(pk=table_order.table.id)
            table.is_reserved = False
            table.save()
            return Response({'msg':'Ready to Pay!'})
        except:
            return Response({'msg':'Internal Error Occured'})
        
def login_view(request,table_id):
    return render(request=request,template_name="login.html")

class TableAdminAPIView(APIView):
    def get(self,request,franchise,outlet):
        blue = "#2c6fbb"
        grey = "#c7c5c5"
        red = "#B33F40"
        green = "#48A14D"

        new = Outlet.objects.get(slug=outlet)
        tables = Table.objects.filter(outlet=new)
        indoor_tables = []
        outdoor_tables = []
        mezzanine_tables = []
        
        unpaid_table_orders = TableOrder.objects.filter(table__in=tables, is_paid=False)

        unpaid_kots = KitchenOrderTicket.objects.filter(table__in=tables, tableorder__in=unpaid_table_orders, is_served=False)

        unserved_orders = Order.objects.filter(
            kitchenorderticket__in=unpaid_kots, is_served=False
            ).annotate(table_number=F('kitchenorderticket__table__table_number'))
        
        
        for table in tables:
            color = blue
            if not table.is_reserved:
                color = grey
            else:
                try:
                    table_order = TableOrder.objects.get(table=table,is_paid=False)
                except TableOrder.DoesNotExist:
                    color = blue
                else:
                    if not table_order.kot.filter(is_served=False).exists():
                        color = blue
                    else:
                        color = red 
                    if table_order.is_paid:
                        color = grey
                        
            if table.category == "IN":
                indoor_tables.append({
                    "table_no": "IN"+str(table.table_number),
                    "id": table.id,
                    "table_color": color,
                    "table_type": "Indoor"
                })
            elif table.category == "OU":
                outdoor_tables.append({
                    "table_no": "OU"+str(table.table_number),
                    "id": table.id,
                    "table_color": color,
                    "table_type": "Outdoor"
                })
            elif table.category == "MZ":
                mezzanine_tables.append({
                    "table_no": "MZ"+str(table.table_number),
                    "id": table.id,
                    "table_color": color,
                    "table_type": "Mezzanine"
                })

        context = {
            "tables":[outdoor_tables,indoor_tables,mezzanine_tables],
            "franchise":franchise, "outlet": outlet,
            "orders":unserved_orders,
        }
        
        return Response(context)
    
    
class FranchiseLoginAPIView(APIView):
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        if username and password:
            user = authenticate(username=username,password=password)
            if user:
                return Response(get_tokens_for_user(user))
            else:
                return Response({'msg':'Unauthorized Successfully'})
        else:
            return Response({'msg':'Details not Provided'})