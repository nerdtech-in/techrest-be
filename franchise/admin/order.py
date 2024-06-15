from rest_framework.views import APIView
from ..models import Order,TableOrder,KitchenOrderTicket
from rest_framework import viewsets,status
from rest_framework.response import Response
from .serializers.order import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
class KitchenOrderTicketAPIView(APIView):
    def delete(self,request,id):
        try:
            kot = KitchenOrderTicket.objects.get(id=id)
            for order in kot.order.all():
                order.delete()
            kot.delete()
        except:
            return Response({'msg':'Kot not Found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'msg':'KOT deleted'})
    