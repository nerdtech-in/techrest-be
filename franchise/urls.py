# urls.py

from django.urls import path, include
from .views import MarkOrderServedView,TableOrderAPIView,TableAPIView,CustomerAPIView,OrderAPIView,orders_view,table_view,show_table_order,CustomerFingerAPIView,PaymentAPIView,MakePaymentAPIView,QRAPIView
from .form_views import create_order,order_success

urlpatterns = [
    path('menu/<str:franchise_slug>/<str:outlet_slug>/<int:table_id>/',TableAPIView.as_view()),
    path('login/',CustomerAPIView.as_view()),
    path('print-login/',CustomerFingerAPIView.as_view()),
    path('order/',OrderAPIView.as_view()),
    path('orders/<franchise>/<outlet>/', orders_view, name='orders_view'),
    path('tables/<franchise>/<outlet>/',table_view,name="table_view"),
    path('tables/<franchise>/<outlet>/table/<int:table_id>',show_table_order,name="table_view"),
    path('mark_order_served/', MarkOrderServedView.as_view(), name='mark-order-served'),
    path('my-order-history/', TableOrderAPIView.as_view(), name='mark-order-served'),
    path('make-payment/', PaymentAPIView.as_view(), name='make_payment'),
    path('make-payment-admin/', MakePaymentAPIView.as_view(), name='make_payment_admin'),
    path('place-order/<int:table_id>/', create_order, name='place-order'),
    path('order-success/', order_success, name='order_success'),
    path('generate-qr/', QRAPIView.as_view(), name='generate_qr'),
]
