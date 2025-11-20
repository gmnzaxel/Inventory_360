from rest_framework import viewsets, serializers
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
from rest_framework.views import APIView
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import calendar
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
import csv
import io
from Inventory360.api_errors import ApiError, ForbiddenError

class BusinessView(viewsets.ReadOnlyModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(id=self.request.user.business_id)

class BranchView(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Branch.objects.filter(business=user.business)
        if user.branch_id:
            return Branch.objects.filter(pk=user.branch_id)
        raise ForbiddenError(
            detail="No tienes una sucursal asignada.",
            code="branch.branch_missing",
            request=self.request
        )

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminUserCustom]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)
        
    def perform_destroy(self, instance):
        branch_count = Branch.objects.filter(business=instance.business).count()
        if branch_count <= 1:
            raise ApiError(detail="No se puede eliminar la ultima sucursal de la empresa.", code="branch.last_branch", request=self.request)
        instance.delete()

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(business=self.request.user.business)

    def get_permissions(self):
        # Allow authenticated users to list/retrieve categories.
        # Require admin for create/update/partial_update/destroy.
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUserCustom()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)

class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.none()
        if user.role == 'admin':
            qs = Product.objects.filter(business=user.business)
            include_all = self.request.query_params.get('include_all', 'false').lower() == 'true'
            if not include_all:
                return qs.filter(stocks__quantity__gt=0).distinct()
            return qs.distinct()
        if getattr(user, 'can_view_products', False):
            if not user.branch_id:
                raise ForbiddenError(
                    detail="No tienes una sucursal asignada.",
                    code="products.branch_missing",
                    request=self.request
                )
            include_all = self.request.query_params.get('include_all', 'false').lower() == 'true'
            qs = Product.objects.filter(
                business=user.business,
                stocks__branch=user.branch
            ).distinct()
            if not include_all:
                qs = qs.filter(stocks__quantity__gt=0)
            return qs
        raise ForbiddenError(
            detail="No tienes permiso para ver productos.",
            code="products.read_forbidden",
            request=self.request
        )

    def perform_create(self, serializer):
        minimum_stock_value = serializer.validated_data.get('minimum_stock_input', 10)
        product = serializer.save(business=self.request.user.business)
        branches = Branch.objects.filter(business=self.request.user.business)
        for branch in branches:
            Stock.objects.create(
                product=product, 
                branch=branch, 
                quantity=0, 
                minimum_stock=minimum_stock_value
            )
    
    def perform_update(self, serializer):
        minimum_stock_value = self.request.data.get('minimum_stock_input')
        product = serializer.save()
        if minimum_stock_value is not None:
            Stock.objects.filter(product=product).update(minimum_stock=int(minimum_stock_value))

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
        if self.action in ['destroy', 'update', 'partial_update', 'create']:
            return [IsAuthenticated(), IsAdminUserCustom()]
        return [IsAuthenticated()]

class MovementView(viewsets.ModelViewSet):
    serializer_class = MovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['movement_type']
    search_fields = ['product__name']

    def get_queryset(self):
        user = self.request.user
        qs = Movement.objects.select_related(
            'product', 'branch', 'branch_from', 'user', 'document'
        )
        if user.role == 'admin':
            qs = qs.filter(branch__business=user.business)
        elif user.role == 'user':
            if user.branch:
                qs = qs.filter(
                    Q(branch=user.branch) |
                    Q(branch_from=user.branch)
                ).distinct()
            else:
                raise ForbiddenError(
                    detail="No tienes una sucursal asignada.",
                    code="movements.branch_missing",
                    request=self.request
                )
        else:
            qs = qs.none()

        # Optional date range filters used by the frontend list views
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            qs = qs.filter(date__date__gte=start)
        if end:
            qs = qs.filter(date__date__lte=end)

        return qs.order_by('-date')

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsAuthenticated(), IsAdminUserCustom()]
        return [IsAuthenticated()]

    def _ensure_user_can_create(self, request):
        user = request.user
        if user.role == 'admin':
            return

        movement_type = (request.data.get('movement_type') or '').lower()
        permission_map = {
            'sale': getattr(user, 'can_sale', False),
            'purchase': getattr(user, 'can_purchase', False),
            'transfer': getattr(user, 'can_transfer', False),
            'adjustment': getattr(user, 'can_adjust', False),
        }
        allowed = permission_map.get(movement_type, False)
        if not allowed:
            raise ForbiddenError(
                detail="No tienes permiso para registrar este movimiento.",
                code="movements.create_forbidden",
                request=request
            )

        branch_id = request.data.get('branch_id')
        branch_from_id = request.data.get('branch_from_id')
        if user.branch_id:
            if branch_id and str(branch_id).isdigit() and int(branch_id) != user.branch_id and movement_type != 'transfer':
                raise ForbiddenError(
                    detail="Solo puedes operar en tu sucursal asignada.",
                    code="movements.branch_forbidden",
                    request=request
                )
            if branch_from_id and str(branch_from_id).isdigit() and int(branch_from_id) != user.branch_id:
                raise ForbiddenError(
                    detail="Solo puedes transferir desde tu sucursal asignada.",
                    code="movements.transfer_origin_forbidden",
                    request=request
                )

    def create(self, request, *args, **kwargs):
        self._ensure_user_can_create(request)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """Export movements as CSV with optional date range and grouping.

        Query params:
        - start: YYYY-MM-DD (inclusive)
        - end: YYYY-MM-DD (inclusive)
        - movement_type: sale|purchase|transfer|adjustment (optional)
        - group_by: day|month|year (optional)
        """
        qs = self.get_queryset()
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        mtype = request.query_params.get('movement_type')
        group_by = request.query_params.get('group_by')

        if mtype:
            qs = qs.filter(movement_type=mtype)
        if start:
            qs = qs.filter(date__date__gte=start)
        if end:
            qs = qs.filter(date__date__lte=end)

        # Prepare CSV
        output = io.StringIO()
        # Prepend BOM for Excel compatibility on Windows
        output.write('\ufeff')
        writer = csv.writer(output)

        filename_parts = ["movements"]
        if group_by:
            filename_parts.append(group_by)
        if start:
            filename_parts.append(f"from-{start}")
        if end:
            filename_parts.append(f"to-{end}")
        if mtype:
            filename_parts.append(mtype)
        filename = "_".join(filename_parts) + ".csv"

        if group_by in ['day', 'month', 'year']:
            if group_by == 'day':
                trunc = TruncDay('date')
                header_period = 'Dia'
            elif group_by == 'month':
                trunc = TruncMonth('date')
                header_period = 'Mes'
            else:
                trunc = TruncYear('date')
                header_period = 'Año'

            agg = (
                qs.annotate(period=trunc)
                  .values('period', 'movement_type')
                  .annotate(
                      total_qty=Sum('quantity'),
                      total_amount=Sum(F('unit_price') * F('quantity')),
                      count=Count('id')
                  )
                  .order_by('period', 'movement_type')
            )
            writer.writerow([header_period, 'Tipo', 'Movimientos', 'Cantidad total', 'Monto total'])
            for row in agg:
                total_amount = row['total_amount'] or 0
                # Ventas suelen negativas; usar valor absoluto para monto
                writer.writerow([
                    row['period'].date() if hasattr(row['period'], 'date') else row['period'],
                    row['movement_type'],
                    row['count'],
                    row['total_qty'],
                    f"{abs(total_amount):.2f}",
                ])
        else:
            writer.writerow(['ID', 'Fecha', 'Tipo', 'Producto', 'Sucursal', 'Desde (origen)', 'Cantidad', 'Precio unitario', 'Monto', 'Usuario'])
            for m in qs.select_related('product', 'branch', 'branch_from'):
                unit_price = m.unit_price or 0
                amount = unit_price * m.quantity
                writer.writerow([
                    m.id,
                    m.date.strftime('%Y-%m-%d %H:%M:%S'),
                    m.movement_type,
                    getattr(m.product, 'name', ''),
                    getattr(m.branch, 'name', ''),
                    getattr(m.branch_from, 'name', ''),
                    m.quantity,
                    f"{unit_price:.2f}",
                    f"{amount:.2f}",
                    getattr(m.user, 'name', '') or getattr(m.user, 'email', ''),
                ])

        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

class StockView(ReadOnlyModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Stock.objects.select_related('product', 'branch').all()
        if user.role == 'admin':
            queryset = queryset.filter(branch__business=user.business)
        elif user.role == 'user' and user.branch:
            queryset = queryset.filter(branch=user.branch)
        elif user.role == 'user':
            raise ForbiddenError(
                detail="No tienes una sucursal asignada.",
                code="stock.branch_missing",
                request=self.request
            )

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

    @action(detail=False, methods=['get'], url_path='low-stock/export')
    def low_stock_export(self, request):
        queryset = self.get_queryset().filter(quantity__lt=F('minimum_stock'))
        output = io.StringIO()
        output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(['Producto', 'Sucursal', 'Cantidad', 'Stock minimo'])
        for stock in queryset.select_related('product', 'branch'):
            writer.writerow([
                getattr(stock.product, 'name', ''),
                getattr(stock.branch, 'name', ''),
                stock.quantity,
                stock.minimum_stock,
            ])
        filename = f"low_stock_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

class DashboardDataView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        business = user.business
        today = timezone.now().date()

        if user.role == 'admin':
            product_queryset = Product.objects.filter(business=business)
            movement_base = Movement.objects.filter(branch__business=business)
        else:
            if not user.branch_id:
                raise ForbiddenError(
                    detail="No tienes una sucursal asignada.",
                    code="dashboard.branch_missing",
                    request=request
                )
            branch = user.branch
            product_queryset = Product.objects.filter(
                business=business,
                stocks__branch=branch,
                stocks__quantity__gt=0
            ).distinct()
            movement_base = Movement.objects.filter(
                Q(branch=branch) | Q(branch_from=branch),
                branch__business=business
            )

        total_products = product_queryset.count()

        sales_this_month = movement_base.filter(
            movement_type='sale',
            branch__business=business,
            date__year=today.year,
            date__month=today.month
        )
        if user.role != 'admin':
            sales_this_month = sales_this_month.filter(branch=user.branch)

        sales_this_month_value = sales_this_month.aggregate(
            total_sales=Sum(F('unit_price') * F('quantity'))
        )['total_sales'] or 0
        sales_this_month_value = abs(sales_this_month_value)

        monthly_sales_count = sales_this_month.count()

        low_stock_items = Stock.objects.filter(
            branch__business=business,
            quantity__lt=F('minimum_stock')
        )
        if user.role != 'admin':
            low_stock_items = low_stock_items.filter(branch=user.branch)

        low_stock_count = low_stock_items.count()

        recent_activity = movement_base.order_by('-date')[:5]
        recent_activity_serializer = MovementSerializer(recent_activity, many=True, context={'request': request})

        sales_performance = []
        for i in range(6):
            month_date = today - relativedelta(months=i)
            month_name = calendar.month_abbr[month_date.month]

            monthly_query = movement_base.filter(
                movement_type='sale',
                date__year=month_date.year,
                date__month=month_date.month
            )
            sales = monthly_query.aggregate(
                total=Sum(F('unit_price') * F('quantity'))
            )['total'] or 0

            sales_performance.append({'name': month_name, 'ventas': abs(sales)})

        sales_performance.reverse()

        data = {
            'total_products': total_products,
            'monthly_sales': sales_this_month_value,
            'monthly_sales_count': monthly_sales_count,
            'low_stock_count': low_stock_count,
            'recent_activity': recent_activity_serializer.data,
            'sales_performance': sales_performance,
            'low_stock_items': StockSerializer(low_stock_items, many=True, context={'request': request}).data,
        }
        return Response(data)







