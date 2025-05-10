from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Business, Branch, Category, Product, Document, Movement, Stock
from .serializer import (
    BusinessSerializer, BranchSerializer, CategorySerializer, ProductSerializer,
    DocumentSerializer, MovementSerializer, StockSerializer
)
from user_control.permissions import IsAdminUserCustom
from rest_framework.decorators import action
from rest_framework.response import Response

class BusinessView(ModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        return Business.objects.filter(id=self.request.user.business.id)

class BranchView(ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        return Branch.objects.filter(business=self.request.user.business)

class CategoryView(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        return Category.objects.filter(business=self.request.user.business)

class ProductView(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Product.objects.filter(business=self.request.user.business)
        return Product.objects.filter(business=self.request.user.business, stocks__branch=self.request.user.branch).distinct()

    def get_serializer(self, *args, **kwargs):
        print(f"ProductView.get_serializer: action={self.action}, args={args}, kwargs={kwargs}")
        # Crear el serializador según si es many=True o no
        if kwargs.get('many', False):
            serializer = ProductSerializer(*args, context={'request': self.request}, many=True)
        else:
            serializer = ProductSerializer(*args, context={'request': self.request}, **kwargs)
        print(f"ProductView.get_serializer: serializer={serializer}")
        # Configurar category_id.queryset solo para escritura y cuando no es many=True
        if (self.action in ['create', 'update', 'partial_update'] and 
            self.request and hasattr(self.request, 'user') and 
            self.request.user.is_authenticated and 
            not kwargs.get('many', False)):
            serializer.fields['category_id'].queryset = Category.objects.filter(business=self.request.user.business)
        return serializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(f"ProductView.list: serializer.data={serializer.data}")
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUserCustom]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class DocumentView(ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        return Document.objects.filter(business=self.request.user.business)

class MovementView(ModelViewSet):
    serializer_class = MovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Movement.objects.filter(branch__business=self.request.user.business)

class StockView(ModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(f"StockView.get_queryset: user_business={self.request.user.business}")
        queryset = Stock.objects.filter(branch__business=self.request.user.business)
        product_id = self.request.query_params.get('product_id')
        if product_id:
            print(f"StockView.get_queryset: filtering by product_id={product_id}")
            queryset = queryset.filter(product_id=product_id)
        print(f"StockView.get_queryset: queryset={queryset}")
        return queryset

    def get_serializer(self, *args, **kwargs):
        print(f"StockView.get_serializer: action={self.action}, args={args}, kwargs={kwargs}")
        # Crear el serializador según si es many=True o no
        if kwargs.get('many', False):
            serializer = StockSerializer(*args, context={'request': self.request}, many=True)
        else:
            serializer = StockSerializer(*args, context={'request': self.request}, **kwargs)
        print(f"StockView.get_serializer: serializer={serializer}")
        # Configurar product_id y branch_id solo para escritura y cuando no es many=True
        if (self.action in ['create', 'update', 'partial_update'] and 
            self.request and hasattr(self.request, 'user') and 
            self.request.user.is_authenticated and 
            not kwargs.get('many', False)):
            serializer.fields['product_id'].queryset = Product.objects.filter(business=self.request.user.business)
            serializer.fields['branch_id'].queryset = Branch.objects.filter(business=self.request.user.business)
        return serializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(f"StockView.list: serializer.data={serializer.data}")
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-product-name/(?P<product_name>[^/.]+)')
    def by_product_name(self, request, product_name=None):
        print(f"StockView.by_product_name: product_name={product_name}")
        stocks = self.get_queryset().filter(product__name__icontains=product_name)
        print(f"StockView.by_product_name: stocks={stocks}")
        serializer = self.get_serializer(stocks, many=True)
        print(f"StockView.by_product_name: serializer.data={serializer.data}")
        return Response(serializer.data)