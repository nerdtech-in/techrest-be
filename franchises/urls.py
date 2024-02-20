from django.urls import path
from .views import FranchiseAPIView

urlpatterns = [
    path('get-franchise/',FranchiseAPIView.as_view(),name="get-franchise")
]
