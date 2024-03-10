# urls.py

from django.urls import path, include
from rest_framework import routers
from .views import CategoryViewSet,TableAPIView,CustomerAPIView,OrderAPIView,orders_view,table_view,show_table_order

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('menu/<str:franchise_slug>/<str:outlet_slug>/<int:table_id>/',TableAPIView.as_view()),
    path('login/',CustomerAPIView.as_view()),
    path('order/',OrderAPIView.as_view()),
    path('orders/<franchise>/<outlet>/', orders_view, name='orders_view'),
    path('tables/<franchise>/<outlet>/',table_view,name="table_view"),
    path('tables/<franchise>/<outlet>/table/<int:table_id>',show_table_order,name="table_view"),
]
