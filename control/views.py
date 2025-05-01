from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Business, Branch, Product, Movement, Stock
from .serializer import *


class BusinessView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Business.objects.filter(id=self.request.user.business_id)
        return Business.objects.none()  # solo los admin pueden ver la empresa

    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise serializers.ValidationError("Solo los administradores pueden crear empresas.")
        serializer.save()

class BranchView(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Branch.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise serializers.ValidationError("Solo los administradores pueden crear sucursales.")
        serializer.save() 

class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'user':
            return Product.objects.none()
        return Product.objects.filter(branch__business=self.request.user.business)

class MovementView(viewsets.ModelViewSet):
    serializer_class = MovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'user':
            return Movement.objects.none()
        return Movement.objects.filter(branch__business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StockView(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'user':
            return Stock.objects.none()
        return Stock.objects.filter(branch__business=self.request.user.business)