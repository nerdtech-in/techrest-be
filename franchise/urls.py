# urls.py

from django.urls import path, include
from rest_framework import routers
from .views import CategoryViewSet,TableAPIView,CustomerAPIView,OrderAPIView,orders_view

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('menu/<str:franchise_slug>/<str:outlet_slug>/<int:table_id>/',TableAPIView.as_view()),
    path('login/',CustomerAPIView.as_view()),
    path('order/',OrderAPIView.as_view()),
    path('orders/<franchise>/<outlet>/', orders_view, name='orders_view'),
]
