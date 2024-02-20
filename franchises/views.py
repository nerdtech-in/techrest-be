from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Franchise
from .serializers import FranchiseSerializer
# Create your views here.

class FranchiseAPIView(APIView):
    def get(self,request):
        franchise = Franchise.objects.all()
        serializer = FranchiseSerializer(franchise,many=True)
        
        return Response(serializer.data)