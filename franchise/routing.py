# routing.py
from django.urls import path
from .consumers import FranchiseOutletConsumer

websocket_urlpatterns = [
    path('ws/<franchise>/<outlet>/', FranchiseOutletConsumer.as_asgi()),
]
