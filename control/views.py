from rest_framework import viewsets, permissions, serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Business, Branch, Product, Movement, Stock, Document, Category, Supplier
from .serializer import (
    BusinessSerializer, BranchSerializer, ProductSerializer,
    MovementSerializer, StockSerializer, DocumentSerializer, CategorySerializer, SupplierSerializer
)
from user_control.permissions import IsAdminUserCustom
from rest_framework.views import APIView
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import calendar
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

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

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUserCustom]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)
        
    def perform_destroy(self, instance):
        branch_count = Branch.objects.filter(business=instance.business).count()
        if branch_count <= 1:
            raise serializers.ValidationError("No se puede eliminar la última sucursal de la empresa.")
        instance.delete()

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
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']

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
        product = serializer.save(business=self.request.user.business)
        branches = Branch.objects.filter(business=self.request.user.business)
        for branch in branches:
            Stock.objects.create(product=product, branch=branch, quantity=0, minimum_stock=10)

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
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['movement_type']

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

class SupplierView(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Supplier.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)

class DashboardDataView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        business = user.business
        today = timezone.now().date()

        total_products = Product.objects.filter(business=business).count()
        sales_this_month = Movement.objects.filter(
            product__business=business,
            movement_type='sale',
            date__year=today.year,
            date__month=today.month
        ).aggregate(
            total_sales=Sum(F('unit_price') * F('quantity'))
        )['total_sales'] or 0
        sales_this_month = abs(sales_this_month)
        
        low_stock_items = Stock.objects.filter(
            product__business=business,
            quantity__lt=F('minimum_stock')
        )
        low_stock_count = low_stock_items.count()
        low_stock_serializer = StockSerializer(low_stock_items, many=True, context={'request': request})
        
        total_transfers = Movement.objects.filter(
            product__business=business,
            movement_type='transfer'
        ).count()

        recent_activity = Movement.objects.filter(product__business=business).order_by('-date')[:5]
        recent_activity_serializer = MovementSerializer(recent_activity, many=True, context={'request': request})
        sales_performance = []
        for i in range(6):
            month_date = today - relativedelta(months=i)
            month_name = calendar.month_abbr[month_date.month]
            
            sales = Movement.objects.filter(
                product__business=business,
                movement_type='sale',
                date__year=month_date.year,
                date__month=month_date.month
            ).aggregate(
                total=Sum(F('unit_price') * F('quantity'))
            )['total'] or 0
            
            sales_performance.append({'name': month_name, 'ventas': abs(sales)})
        
        sales_performance.reverse()

        data = {
            'total_products': total_products,
            'monthly_sales': sales_this_month,
            'low_stock_count': low_stock_count,
            'total_transfers': total_transfers,
            'recent_activity': recent_activity_serializer.data,
            'sales_performance': sales_performance,
            'low_stock_items': low_stock_serializer.data,
        }
        return Response(data)