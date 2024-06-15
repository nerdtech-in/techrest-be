from django.urls import path,include
from .admin.order import KitchenOrderTicketAPIView,OrderViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'order',OrderViewSet,basename='order_viewset')

urlpatterns = [
    path('',include(router.urls)),
    path('kot/<int:id>/',KitchenOrderTicketAPIView.as_view(),name="kot_apiview")
]