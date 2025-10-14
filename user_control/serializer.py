from rest_framework import serializers
import re
from .models import User
from control.models import Business, Branch
from control.serializer import BusinessSerializer as ControlBusinessSerializer, BranchSerializer as ControlBranchSerializer
from Inventory360.api_errors import ApiError


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'address', 'phone']


class AdminRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    business = BusinessSerializer(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'password2', 'business']

    def validate(self, attrs):
        name = (attrs.get('name') or '').strip()
        if len(name) == 0:
            raise serializers.ValidationError({"name": "El nombre es requerido."})
        if len(name) > 60:
            raise serializers.ValidationError({"name": "El nombre no puede exceder 60 caracteres."})

        password = attrs.get('password') or ''
        password2 = attrs.get('password2') or ''
        if password != password2:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        strong = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")
        if not strong.match(password):
            raise serializers.ValidationError({"password": "La contraseña debe tener 8+ caracteres e incluir letras, numeros y un simbolo."})

        business = attrs.get('business') or {}
        if len((business.get('name') or '').strip()) == 0:
            raise serializers.ValidationError({"business": "El nombre de la empresa es requerido."})
        if len(business.get('name') or '') > 100:
            raise serializers.ValidationError({"business": "El nombre de la empresa no puede exceder 100 caracteres."})
        if len(business.get('address') or '') > 200:
            raise serializers.ValidationError({"business": "La direccion no puede exceder 200 caracteres."})
        if len(business.get('phone') or '') > 30:
            raise serializers.ValidationError({"business": "El telefono no puede exceder 30 caracteres."})
        return attrs

    def create(self, validated_data):
        business_data = validated_data.pop('business')
        password = validated_data.pop('password')
        validated_data.pop('password2')

        business = Business.objects.create(**business_data)
        Branch.objects.create(
            business=business,
            name="Casa Central",
            address=business_data['address'],
            phone=business_data['phone']
        )

        user = User.objects.create_user(
            role='admin',
            business=business,
            password=password,
            can_purchase=True,
            can_sale=True,
            can_adjust=True,
            can_transfer=True,
            can_view_products=True,
            **validated_data
        )
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source='branch',
        write_only=True,
        required=False,
        allow_null=True,
        help_text="Sucursal a la que pertenece el empleado."
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'password', 'password2', 'role',
            'branch_id', 'can_view_products', 'can_purchase', 'can_sale',
            'can_adjust', 'can_transfer'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated and 'branch_id' in self.fields:
            self.fields['branch_id'].queryset = Branch.objects.filter(business=request.user.business)

    def validate(self, attrs):
        name = (attrs.get('name') or '').strip()
        if len(name) == 0:
            raise serializers.ValidationError({"name": "El nombre es requerido."})
        if len(name) > 60:
            raise serializers.ValidationError({"name": "El nombre no puede exceder 60 caracteres."})

        password = attrs.get('password') or ''
        password2 = attrs.get('password2') or ''
        if password != password2:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        strong = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")
        if not strong.match(password):
            raise serializers.ValidationError({"password": "La contraseña debe tener 8+ caracteres e incluir letras, numeros y un simbolo."})

        role = attrs.get('role') or 'user'
        branch = attrs.get('branch')
        request = self.context.get('request')
        business = getattr(request.user, 'business', None) if request and request.user.is_authenticated else None
        if role != 'admin' and branch is None:
            raise serializers.ValidationError({"branch_id": "Debes asignar una sucursal al empleado."})
        if branch and business and branch.business_id != business.id:
            raise serializers.ValidationError({"branch_id": "La sucursal seleccionada no pertenece a tu empresa."})
        if role == 'admin':
            attrs['can_view_products'] = True
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    business = ControlBusinessSerializer(read_only=True)
    branch = ControlBranchSerializer(read_only=True)
    permissions = serializers.SerializerMethodField()
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source='branch',
        write_only=True,
        required=False,
        allow_null=True,
        help_text="Sucursal a la que pertenece el empleado."
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'role', 'business', 'branch', 'branch_id',
            'can_view_products', 'can_purchase', 'can_sale',
            'can_adjust', 'can_transfer', 'permissions'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated and 'branch_id' in self.fields:
            self.fields['branch_id'].queryset = Branch.objects.filter(business=request.user.business)

    def validate(self, attrs):
        role = attrs.get('role')
        if role is None and self.instance:
            role = self.instance.role

        branch = attrs.get('branch', serializers.empty)
        if branch is serializers.empty and self.instance:
            branch = self.instance.branch

        request = self.context.get('request')
        business = getattr(request.user, 'business', None) if request and request.user.is_authenticated else None

        if role != 'admin' and branch is None:
            raise serializers.ValidationError({"branch_id": "Debes asignar una sucursal al empleado."})
        if branch and business and branch.business_id != business.id:
            raise serializers.ValidationError({"branch_id": "La sucursal seleccionada no pertenece a tu empresa."})
        if role == 'admin':
            attrs['branch'] = None
        return attrs

    def get_permissions(self, obj):
        return obj.permission_codes


