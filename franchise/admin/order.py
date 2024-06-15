from rest_framework.views import APIView
from ..models import Order,TableOrder,KitchenOrderTicket
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers.order import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
class KitchenOrderTicketAPIView(APIView):
    def delete(self,request,id):
        # get pertcaular kot
        kot = KitchenOrderTicket.objects.get(id=id)
        # delete all the orders related to KOT
        for order in kot.order.all():
            order.delete()
        # delete the kot
        kot.delete()
        return Response()