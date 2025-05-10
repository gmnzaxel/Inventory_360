from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Business, Branch, Product, Movement, Stock, Document, Category

# Validador para campos de texto (solo letras, espacios, guiones, apóstrofes, tildes y ñ)
text_only_validator = RegexValidator(
    regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$',
    message='Este campo solo puede contener letras, espacios, guiones, apóstrofes o caracteres en español (como tildes y ñ).'
)

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['business'].queryset = Business.objects.filter(id=request.user.business_id)
    def create(self, validated_data):
        validated_data['business'] = self.context['request'].user.business
        return super().create(validated_data)

class ProductSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    business_id = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all(), source='business', write_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True)
    name = serializers.CharField(validators=[text_only_validator])
    description = serializers.CharField(validators=[text_only_validator])
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_id', 'business', 'business_id']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['business_id'].queryset = Business.objects.filter(id=request.user.business_id)
            self.fields['category_id'].queryset = Category.objects.filter(business=request.user.business)

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

class MovementSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch', write_only=True)
    branch_from = BranchSerializer(read_only=True)
    branch_from_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch_from', write_only=True, required=False, allow_null=True)
    user = serializers.ReadOnlyField(source='user.email')
    document = DocumentSerializer(read_only=True)
    document_id = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all(), source='document', write_only=True, required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=0, error_messages={
        'min_value': 'La cantidad no puede ser negativa.',
        'invalid': 'La cantidad debe ser un número entero.'
    })
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    class Meta:
        model = Movement
        fields = ['id', 'movement_type', 'quantity', 'date', 'product', 'product_id', 'branch', 'branch_id', 'branch_from', 'branch_from_id', 'user', 'document', 'document_id', 'unit_price']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            self.fields['product_id'].queryset = Product.objects.filter(business=user.business)
            self.fields['branch_id'].queryset = Branch.objects.filter(business=user.business)
            self.fields['branch_from_id'].queryset = Branch.objects.filter(business=user.business)
            self.fields['document_id'].queryset = Document.objects.filter(business=user.business)
    def validate(self, data):
        product = data['product']
        branch = data['branch']
        branch_from = data.get('branch_from')
        quantity = data['quantity']
        user = self.context['request'].user
        movement_type = data['movement_type']
        document = data.get('document')
        unit_price = data.get('unit_price')
        # Validar correspondencia entre document_type y movement_type
        if document:
            valid_types = {
                'sale': 'invoice',
                'purchase': 'purchase_order',
                'adjustment': 'adjustment_note',
                'transfer': 'transfer_note'
            }
            if document.document_type != valid_types.get(movement_type):
                raise serializers.ValidationError(f"El documento debe ser de tipo '{valid_types[movement_type]}' para movimientos de tipo '{movement_type}'.")
        # Validar unit_price
        if movement_type in ['purchase', 'sale'] and not unit_price:
            raise serializers.ValidationError("El precio unitario es requerido para compras y ventas.")
        if movement_type in ['adjustment', 'transfer'] and unit_price:
            raise serializers.ValidationError("El precio unitario no debe especificarse para ajustes o transferencias.")
        # Validar que el producto y las sucursales pertenezcan a la empresa del usuario
        if product.business != user.business or branch.business != user.business:
            raise serializers.ValidationError("El producto o la sucursal no pertenecen a tu empresa.")
        if branch_from and branch_from.business != user.business:
            raise serializers.ValidationError("La sucursal de origen no pertenece a tu empresa.")
        # Validar permisos granulares
        if movement_type == 'purchase' and not user.can_purchase:
            raise serializers.ValidationError("No tienes permiso para registrar compras.")
        if movement_type == 'sale' and not user.can_sale:
            raise serializers.ValidationError("No tienes permiso para registrar ventas.")
        if movement_type == 'adjustment' and not user.can_adjust:
            raise serializers.ValidationError("No tienes permiso para registrar ajustes.")
        if movement_type == 'transfer' and not user.can_transfer:
            raise serializers.ValidationError("No tienes permiso para registrar transferencias.")
        # Validar el documento si se proporciona
        if document and document.business != user.business:
            raise serializers.ValidationError("El documento no pertenece a tu empresa.")
        # Validar stock suficiente para movimientos de salida
        if movement_type == 'sale' or (movement_type == 'adjustment' and quantity < 0):
            try:
                stock = Stock.objects.get(product=product, branch=branch)
                if stock.quantity < abs(quantity):
                    raise serializers.ValidationError(f"Stock insuficiente. Disponible: {stock.quantity}")
            except Stock.DoesNotExist:
                raise serializers.ValidationError("No hay stock registrado para este producto en esta sucursal.")
        # Validar transferencias
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
        movement = super().create(validated_data)
        product = movement.product
        branch = movement.branch
        branch_from = movement.branch_from
        quantity = movement.quantity
        movement_type = movement.movement_type
        # Actualizar el stock
        stock_to, _ = Stock.objects.get_or_create(product=product, branch=branch, defaults={'quantity': 0, 'minimum_stock': 0})
        if movement_type == 'purchase' or (movement_type == 'adjustment' and quantity > 0):
            stock_to.quantity += quantity
        elif movement_type == 'sale' or (movement_type == 'adjustment' and quantity < 0):
            stock_to.quantity -= abs(quantity)
        elif movement_type == 'transfer':
            if branch_from:
                stock_from, _ = Stock.objects.get_or_create(product=product, branch=branch_from, defaults={'quantity': 0, 'minimum_stock': 0})
                if stock_from.quantity >= quantity:
                    stock_from.quantity -= quantity
                    stock_from.save()
                stock_to.quantity += quantity
        stock_to.save()
        return movement

class StockSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch', write_only=True)
    quantity = serializers.ReadOnlyField()
    minimum_stock = serializers.IntegerField(min_value=0, error_messages={
        'min_value': 'El stock mínimo no puede ser negativo.',
        'invalid': 'El stock mínimo debe ser un número entero.'
    })
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