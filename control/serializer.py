from rest_framework import serializers
from .models import Business, Branch, Product, Movement, Stock, Document, Category, Supplier
from django.db.models import Sum, Min

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'phone', 'business']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'business']
        read_only_fields = ['business']

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'image']

class ProductSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    stock = serializers.SerializerMethodField()
    minimum_stock = serializers.SerializerMethodField()
    minimum_stock_input = serializers.IntegerField(write_only=True, required=False, default=10)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_id', 'business', 'stock', 'minimum_stock', 'minimum_stock_input', 'image']

    def get_stock(self, obj):
        total = obj.stocks.aggregate(total_stock=Sum('quantity'))['total_stock']
        return total or 0
    
    def get_minimum_stock(self, obj):
        agg = obj.stocks.aggregate(min_value=Min('minimum_stock'))['min_value']
        return agg if agg is not None else 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if 'category_id' in self.fields:
                self.fields['category_id'].queryset = Category.objects.filter(business=request.user.business)
    
    def create(self, validated_data):
        validated_data.pop('minimum_stock_input', None)
        validated_data['business'] = self.context['request'].user.business
        return super().create(validated_data)

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'document_number', 'date', 'business', 'created_by']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['business'].queryset = Business.objects.filter(id=request.user.business_id)
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['business'] = self.context['request'].user.business
        return super().create(validated_data)

class SupplierSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'phone', 'email', 'business']
        read_only_fields = ['business']

class MovementSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch', write_only=True)
    branch_from = BranchSerializer(read_only=True)
    branch_from_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch_from', write_only=True, required=False, allow_null=True)
    user = serializers.ReadOnlyField(source='user.name')
    document = DocumentSerializer(read_only=True)
    document_id = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all(), source='document', write_only=True, required=False, allow_null=True)
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), source='supplier', write_only=True, required=False, allow_null=True)
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    
    class Meta:
        model = Movement
        fields = [
            'id', 'movement_type', 'quantity', 'date', 'product', 
            'product_id', 'branch', 'branch_id', 'branch_from', 
            'branch_from_id', 'user', 'document', 'document_id', 
            'unit_price', 'supplier', 'supplier_id', 'notes'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            self.fields['product_id'].queryset = Product.objects.filter(business=user.business)
            self.fields['branch_id'].queryset = Branch.objects.filter(business=user.business)
            self.fields['branch_from_id'].queryset = Branch.objects.filter(business=user.business)
            self.fields['document_id'].queryset = Document.objects.filter(business=user.business)
            self.fields['supplier_id'].queryset = Supplier.objects.filter(business=user.business)

    def validate(self, data):
        product = data['product']
        branch = data['branch']
        branch_from = data.get('branch_from')
        quantity = data['quantity']
        user = self.context['request'].user
        movement_type = data['movement_type']
        document = data.get('document')
        unit_price = data.get('unit_price')
        if document:
            valid_types = {
                'sale': 'invoice',
                'purchase': 'purchase_order',
                'adjustment': 'adjustment_note',
                'transfer': 'transfer_note'
            }
            if document.document_type != valid_types.get(movement_type):
                raise serializers.ValidationError(f"El documento debe ser de tipo '{valid_types[movement_type]}' para movimientos de tipo '{movement_type}'.")
        if movement_type in ['purchase', 'sale'] and not unit_price:
            raise serializers.ValidationError("El precio unitario es requerido para compras y ventas.")
        if movement_type in ['adjustment', 'transfer'] and unit_price:
            raise serializers.ValidationError("El precio unitario no debe especificarse para ajustes o transferencias.")
        # Quantity rules by movement type
        if movement_type in ['purchase', 'transfer'] and quantity <= 0:
            raise serializers.ValidationError("La cantidad debe ser positiva para compras y transferencias.")
        if movement_type in ['sale', 'adjustment'] and quantity == 0:
            raise serializers.ValidationError("La cantidad no puede ser 0.")
        if product.business != user.business or branch.business != user.business:
            raise serializers.ValidationError("El producto o la sucursal no pertenecen a tu empresa.")
        if branch_from and branch_from.business != user.business:
            raise serializers.ValidationError("La sucursal de origen no pertenece a tu empresa.")
        if movement_type == 'purchase' and not user.can_purchase:
            raise serializers.ValidationError("No tienes permiso para registrar compras.")
        if movement_type == 'sale' and not user.can_sale:
            raise serializers.ValidationError("No tienes permiso para registrar ventas.")
        if movement_type == 'adjustment' and not user.can_adjust:
            raise serializers.ValidationError("No tienes permiso para registrar ajustes.")
        if movement_type == 'transfer' and not user.can_transfer:
            raise serializers.ValidationError("No tienes permiso para registrar transferencias.")
        if document and document.business != user.business:
            raise serializers.ValidationError("El documento no pertenece a tu empresa.")
        if movement_type == 'sale' or (movement_type == 'adjustment' and quantity < 0):
            try:
                stock = Stock.objects.get(product=product, branch=branch)
                if stock.quantity < abs(quantity):
                    raise serializers.ValidationError(f"Stock insuficiente. Disponible: {stock.quantity}")
            except Stock.DoesNotExist:
                raise serializers.ValidationError("No hay stock registrado para este producto en esta sucursal.")
        if movement_type == 'transfer':
            if not branch_from or branch == branch_from:
                raise serializers.ValidationError("Debes especificar una sucursal de origen diferente a la de destino.")
            try:
                stock_from = Stock.objects.get(product=product, branch=branch_from)
                if stock_from.quantity < abs(quantity):
                    raise serializers.ValidationError(f"Stock insuficiente en la sucursal de origen. Disponible: {stock_from.quantity}")
            except Stock.DoesNotExist:
                raise serializers.ValidationError("No hay stock registrado en la sucursal de origen.")
        return data

    def create(self, validated_data):
        movement_type = validated_data.get('movement_type')
        quantity = validated_data.get('quantity')
        
        if movement_type == 'sale':
            validated_data['quantity'] = -abs(quantity)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Normalize quantity sign on updates as well (e.g., sales stay negative)."""
        movement_type = validated_data.get('movement_type', instance.movement_type)
        if movement_type == 'sale':
            qty = validated_data.get('quantity')
            if qty is not None:
                validated_data['quantity'] = -abs(qty)
        return super().update(instance, validated_data)

class StockSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch', write_only=True)
    quantity = serializers.ReadOnlyField()
    minimum_stock = serializers.IntegerField(min_value=0)
    is_low_stock = serializers.SerializerMethodField()
    
    def get_is_low_stock(self, obj):
        return obj.quantity < obj.minimum_stock
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['product_id'].queryset = Product.objects.filter(business=request.user.business)
            self.fields['branch_id'].queryset = Branch.objects.filter(business=request.user.business)
            
    class Meta:
        model = Stock
        fields = ['id', 'product', 'product_id', 'branch', 'branch_id', 'quantity', 'minimum_stock', 'is_low_stock']

