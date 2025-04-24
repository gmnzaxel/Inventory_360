# control/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Business, Category, Product, Supplier, Movement
from .serializer import (
    BusinessSerializer,
    CategorySerializer,
    ProductSerializer,
    SupplierSerializer,
    MovementSerializer
)

class BusinessView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class SupplierView(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

class MovementView(viewsets.ModelViewSet):
    queryset = Movement.objects.all()
    serializer_class = MovementSerializer
    permission_classes = [IsAuthenticated]

