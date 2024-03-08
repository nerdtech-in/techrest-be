import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from franchise.routing import websocket_urlpatterns
from django.urls import path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techrest.settings')

django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    'http':django_asgi_app,
    'websocket':AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})