from .import *


class SearchAPIView(APIView):
    class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    def get(self,request):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        field = self.request.query_params.get('field', None)

        if search_query and field in ['id', 'name']:
            if field == 'id':
                queryset = queryset.filter(id=search_query)
            elif field == 'name':
                queryset = queryset.filter(name__icontains=search_query)