from django.urls import path

from .views import *
urlpatterns = [
    path('menu/<str:franchise_slug>/<str:outlet_slug>/<int:table_id>/',MenuAPIView.as_view())
]
