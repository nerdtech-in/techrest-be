from rest_framework import serializers
from .models import Order,KitchenOrderTicket,TableOrder

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class KitchenOrderTicketSerializer(serializers.ModelSerializer):
    order = OrderSerializer(many=True)
    class Meta:
        model = KitchenOrderTicket
        fields = '__all__'

class TableOrderSerializer(serializers.ModelSerializer):
    kot = KitchenOrderTicketSerializer(many=True, read_only=True)

    class Meta:
        model = TableOrder
        fields = '__all__'
