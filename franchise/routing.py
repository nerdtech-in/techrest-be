# routing.py
from django.urls import path
from .consumers import FranchiseOutletConsumer,TableStatusConsumer

websocket_urlpatterns = [
    path('ws/<franchise>/<outlet>/', FranchiseOutletConsumer.as_asgi()),
    path('ws/tables/<franchise>/<outlet>/', TableStatusConsumer.as_asgi()),
]
