from rest_framework import viewsets, permissions, serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Business, Branch, Product, Movement, Stock, Document, Category
from .serializer import (
    BusinessSerializer, BranchSerializer, ProductSerializer,
    MovementSerializer, StockSerializer, DocumentSerializer, CategorySerializer
)
from user_control.permissions import IsAdminUserCustom

class BusinessView(viewsets.ReadOnlyModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(id=self.request.user.business_id)

class BranchView(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        return Branch.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        return Category.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)

class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Product.objects.filter(business=user.business)
        elif user.role == 'user' and user.branch:
            return Product.objects.filter(business=user.business, stocks__branch=user.branch).distinct()
        return Product.objects.none()

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsAuthenticated(), IsAdminUserCustom()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        business = serializer.validated_data.get('business')
        if business != self.request.user.business:
            raise serializers.ValidationError("No puedes asignar un producto a otra empresa.")
        serializer.save()

class DocumentView(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Document.objects.filter(business=user.business)
        elif user.role == 'user' and user.branch:
            return Document.objects.filter(business=user.business)
        return Document.objects.none()

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsAuthenticated(), IsAdminUserCustom()]
        return [IsAuthenticated()]

class MovementView(viewsets.ModelViewSet):
    serializer_class = MovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Movement.objects.filter(branch__business=user.business)
        elif user.role == 'user' and user.branch:
            return Movement.objects.filter(branch=user.branch)
        return Movement.objects.none()

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsAuthenticated(), IsAdminUserCustom()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        branch = serializer.validated_data.get('branch')
        product = serializer.validated_data.get('product')
        if branch.business != self.request.user.business or product.business != self.request.user.business:
            raise serializers.ValidationError("Sucursal o producto no pertenecen a tu empresa.")
        serializer.save(user=self.request.user)

class StockView(ReadOnlyModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Stock.objects.all()
        if user.role == 'admin':
            queryset = queryset.filter(branch__business=user.business)
        elif user.role == 'user' and user.branch:
            queryset = queryset.filter(branch=user.branch)

        product_id = self.request.query_params.get('product_id', None)
        branch_id = self.request.query_params.get('branch_id', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        return queryset

    def get_permissions(self):
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='by-product-name/(?P<product_name>[^/.]+)')
    def by_product_name(self, request, product_name=None):
        queryset = self.get_queryset().filter(product__name__iexact=product_name)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)