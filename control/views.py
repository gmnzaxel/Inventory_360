from rest_framework import viewsets, permissions, serializers
from rest_framework.permissions import IsAuthenticated
from .models import Business, Branch, Product, Movement, Stock
from .serializer import *

class BusinessView(viewsets.ReadOnlyModelViewSet): 
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(id=self.request.user.business_id)

class BranchView(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Branch.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise serializers.ValidationError("Solo los administradores pueden crear sucursales.")
        serializer.save(business=self.request.user.business)

class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(branch__business=self.request.user.business)

class MovementView(viewsets.ModelViewSet):
    serializer_class = MovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Movement.objects.filter(branch__business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StockView(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Stock.objects.filter(branch__business=self.request.user.business)
