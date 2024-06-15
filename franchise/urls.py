from django.urls import path, include
from .views import *
from .form_views import create_order, order_success

urlpatterns = [
    path('menu/<str:franchise_slug>/<str:outlet_slug>/<int:table_id>/', TableAPIView.as_view(), name='table_api_view'),
    path('menu/<str:franchise_slug>/<str:outlet_slug>/', MenuAPIView.as_view(), name='menu_api_view'),
    path('franchise-login/', FranchiseLoginAPIView.as_view(), name='franchise_login'),
    path('login/', CustomerAPIView.as_view(), name='customer_login'),
    path('print-login/', CustomerFingerAPIView.as_view(), name='print_login'),
    path('order/', OrderAPIView.as_view(), name='order_api_view'),
    path('orders/<str:franchise>/<str:outlet>/', orders_view, name='orders_view'),
    path('tables/<str:franchise>/<str:outlet>/', table_view, name='tables_view'),
    path('tables/<str:franchise>/<str:outlet>/table/<int:table_id>/', show_table_order, name='show_table_order'),
    path('mark_order_served/', MarkOrderServedView.as_view(), name='mark_order_served'),
    path('my-order-history/', TableOrderAPIView.as_view(), name='my_order_history'),
    path('make-payment/', PaymentAPIView.as_view(), name='make_payment'),
    path('make-payment-admin/', MakePaymentAPIView.as_view(), name='make_payment_admin'),
    path('place-order/<int:table_id>/', create_order, name='place_order'),
    path('order-success/', order_success, name='order_success'),
    path('generate-qr/', QRAPIView.as_view(), name='generate_qr'),
    path('ready-to-pay/', MakePaymentAPIView.as_view(), name='ready_to_pay'),
    path('customer-login/<int:table_id>/', login_view, name='customer_login_table'),
    path('tables-view/<str:franchise>/<str:outlet>/', TableAdminAPIView.as_view(), name='tables_view_admin'),
    path('get-table-order/<int:table_id>/', GetOrderAPIView.as_view(), name='get_table_order'),
]






















# # urls.py

# from django.urls import path, include
# from .views import *
# from .form_views import create_order,order_success

# urlpatterns = [
#     path('menu/<str:franchise_slug>/<str:outlet_slug>/<int:table_id>/',TableAPIView.as_view()),
#     path('menu/<str:franchise_slug>/<str:outlet_slug>/',MenuAPIView.as_view()),
#     path('franchise-login/',FranchiseLoginAPIView.as_view()),
#     path('login/',CustomerAPIView.as_view()),
#     path('print-login/',CustomerFingerAPIView.as_view()),
#     path('order/',OrderAPIView.as_view()),
#     path('orders/<franchise>/<outlet>/', orders_view, name='orders_view'),
#     path('tables/<franchise>/<outlet>/',table_view,name="table_view"),
#     path('tables/<franchise>/<outlet>/table/<int:table_id>',show_table_order,name="table_view"),
#     path('mark_order_served/', MarkOrderServedView.as_view(), name='mark-order-served'),
#     path('my-order-history/', TableOrderAPIView.as_view(), name='mark-order-served'),
#     path('make-payment/', PaymentAPIView.as_view(), name='make_payment'),
#     path('make-payment-admin/', MakePaymentAPIView.as_view(), name='make_payment_admin'),
#     path('place-order/<int:table_id>/', create_order, name='place-order'),
#     path('order-success/', order_success, name='order_success'),
#     path('generate-qr/', QRAPIView.as_view(), name='generate_qr'),
#     path('ready-to-pay/', MakePaymentAPIView.as_view(), name='ready_to_pay'),
#     path('customer-login/<int:table_id>/', login_view, name='login'),
#     path('tables-view/<str:franchise>/<str:outlet>/', TableAdminAPIView.as_view(), name='table-view'),
#     path('get-table-order/<int:table_id>', GetOrderAPIView.as_view(), name='table-view'),
# ]
