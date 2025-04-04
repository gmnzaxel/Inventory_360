from django.shortcuts import render
from rest_framework import viewsets
from .serializer import *
from .models import *



class BussinesView(viewsets.ModelViewSet):
    serializer_class = BussinesSerializer
    queryset = Bussines.objects.all()

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    
class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
class SupplierView(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()
    
class MovementView(viewsets.ModelViewSet):
    serializer_class = MovementSerializer
    queryset = Movement.objects.all()
