from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Business, Branch, Category, Product, Document, Movement, Stock
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'address', 'phone', 'notes']

    def validate_phone(self, value):
        phone_regex = r'^\d{10}$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError("El teléfono debe tener 10 dígitos numéricos.")
        return value

class BranchSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^\d{10}$',
            message="El teléfono debe tener 10 dígitos numéricos."
        )]
    )

    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'phone', 'business']
        extra_kwargs = {'business': {'required': False}}

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_business = request.user.business
            if 'business' in data and data['business'] != user_business:
                raise serializers.ValidationError("No puedes asignar una sucursal a otra empresa.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['business'] = request.user.business
        return super().create(validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'business']
        extra_kwargs = {'business': {'required': False}}

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_business = request.user.business
            if 'business' in data and data['business'] != user_business:
                raise serializers.ValidationError("No puedes asignar una categoría a otra empresa.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['business'] = request.user.business
        return super().create(validated_data)

class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')
    price = serializers.FloatField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'business', 'category', 'category_id']
        extra_kwargs = {'business': {'required': False}}

    def validate_name(self, value):
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError("Este campo solo puede contener letras y espacios.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que cero.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_business = request.user.business
            category = data.get('category')
            if category and user_business and category.business != user_business:
                print(f"ProductSerializer.validate: user_business={user_business}, category_business={category.business}")
                raise serializers.ValidationError("No puedes asignar un producto a otra empresa.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['business'] = request.user.business
        return super().create(validated_data)

class DocumentSerializer(serializers.ModelSerializer):
    document_number = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^[A-Z0-9\-]+$',
            message="El número de documento solo puede contener letras, números y guiones."
        )]
    )

    class Meta:
        model = Document
        fields = ['id', 'document_type', 'document_number', 'business', 'created_by']
        read_only_fields = ['created_by', 'business']

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            document_type = data.get('document_type')
            document_number = data.get('document_number')
            if Document.objects.filter(document_type=document_type, document_number=document_number, business=request.user.business).exists():
                raise serializers.ValidationError({"document_number": "Ya existe un documento con este tipo y número en la empresa."})
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['business'] = request.user.business
            validated_data['created_by'] = request.user
        return super().create(validated_data)

class MovementSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch', write_only=True)
    document_id = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all(), source='document', write_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    branch = serializers.PrimaryKeyRelatedField(read_only=True)
    document = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Movement
        fields = ['id', 'movement_type', 'quantity', 'unit_price', 'product', 'product_id', 'branch', 'branch_id', 'document', 'document_id', 'user']
        read_only_fields = ['user', 'product', 'branch', 'document']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            self.fields['product_id'].queryset = Product.objects.filter(business=request.user.business)
            self.fields['branch_id'].queryset = Branch.objects.filter(business=request.user.business)
            self.fields['document_id'].queryset = Document.objects.filter(business=request.user.business)

    def to_internal_value(self, data):
        print(f"MovementSerializer.to_internal_value: data={data}")
        validated_data = super().to_internal_value(data)
        print(f"MovementSerializer.to_internal_value: validated_data={validated_data}")
        return validated_data

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value

    def validate(self, data):
        print(f"MovementSerializer.validate: data={data}")
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            raise serializers.ValidationError("Usuario no autenticado.")

        user = request.user
        movement_type = data.get('movement_type')
        product = data.get('product')
        branch = data.get('branch')
        document = data.get('document')
        quantity = data.get('quantity')
        unit_price = data.get('unit_price')

        if movement_type == 'sale' and not user.can_sale:
            raise serializers.ValidationError("No tienes permiso para registrar ventas.")
        if movement_type == 'purchase' and not user.can_purchase:
            raise serializers.ValidationError("No tienes permiso para registrar compras.")
        if movement_type == 'adjustment' and not user.can_adjust:
            raise serializers.ValidationError("No tienes permiso para registrar ajustes.")
        if movement_type == 'transfer' and not user.can_transfer:
            raise serializers.ValidationError("No tienes permiso para registrar transferencias.")

        if movement_type == 'sale' and document.document_type not in ['invoice', 'credit_note']:
            raise serializers.ValidationError("El documento debe ser de tipo 'invoice' o 'credit_note' para ventas.")
        if movement_type == 'purchase' and document.document_type not in ['purchase_order', 'invoice']:
            raise serializers.ValidationError("El documento debe ser de tipo 'purchase_order' o 'invoice' para compras.")
        if movement_type == 'adjustment' and document.document_type != 'adjustment':
            raise serializers.ValidationError("El documento debe ser de tipo 'adjustment' para ajustes.")
        if movement_type == 'transfer' and document.document_type != 'transfer':
            raise serializers.ValidationError("El documento debe ser de tipo 'transfer' para transferencias.")

        if movement_type in ['purchase', 'transfer', 'adjustment'] and unit_price is None:
            raise serializers.ValidationError("El precio unitario es requerido para compras, transferencias o ajustes.")

        if product.business != user.business or branch.business != user.business or document.business != user.business:
            raise serializers.ValidationError("El producto, la sucursal y el documento deben pertenecer a la misma empresa que el usuario.")

        try:
            stock = Stock.objects.get(product=product, branch=branch)
            if movement_type == 'sale' and stock.quantity < quantity:
                raise serializers.ValidationError(f"Stock insuficiente: solo hay {stock.quantity} unidades disponibles.")
        except Stock.DoesNotExist:
            if movement_type == 'sale':
                raise serializers.ValidationError("No hay stock disponible para este producto en la sucursal.")

        return data

class StockSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(), source='branch', write_only=True
    )
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ['id', 'product', 'product_id', 'branch', 'branch_id', 'quantity', 'minimum_stock', 'is_low_stock']
        extra_kwargs = {
            'product': {'required': False},
            'branch': {'required': False}
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Stock.objects.all(),
                fields=('product', 'branch')
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            self.fields['product_id'].queryset = Product.objects.filter(business=request.user.business)
            self.fields['branch_id'].queryset = Branch.objects.filter(business=request.user.business)

    def get_is_low_stock(self, obj):
        if isinstance(obj, Stock):
            return obj.quantity <= obj.minimum_stock
        return False

    def validate_minimum_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock mínimo no puede ser negativo.")
        return value

    def to_internal_value(self, data):
        print(f"StockSerializer.to_internal_value: data={data}")
        validated_data = super().to_internal_value(data)
        print(f"StockSerializer.to_internal_value: validated_data={validated_data}")
        return validated_data

    def validate(self, data):
        print(f"StockSerializer.validate: data={data}")
        print(f"StockSerializer.validate: product_id_queryset={self.fields['product_id'].queryset.filter(id=data.get('product').id).exists()}")
        print(f"StockSerializer.validate: branch_id_queryset={self.fields['branch_id'].queryset.filter(id=data.get('branch').id).exists()}")
        return data