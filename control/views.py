from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Business, Branch, Product, Movement, Stock
from .serializer import (
    BusinessSerializer,
    ProductSerializer,
    MovementSerializer,
    BranchSerializer,
    StockSerializer
)

class BusinessView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

class BranchView(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]    

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class MovementView(viewsets.ModelViewSet):
    queryset = Movement.objects.all().order_by('-date')
    serializer_class = MovementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StockView(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]