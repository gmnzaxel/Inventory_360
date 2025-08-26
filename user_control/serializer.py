from rest_framework import serializers
from .models import User
from control.models import Business, Branch
import re
from control.serializer import BranchSerializer

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'address', 'phone']

class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    business = BusinessSerializer(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'username', 'password', 'password2', 'business']
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
            'username': {'required': True}
        }

    def validate_name(self, value):
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("El nombre no debe contener números.")
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra minúscula.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un símbolo (ej: !@#$%&*?).")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        business_data = validated_data.pop('business')
        
        business = Business.objects.create(**business_data)
        Branch.objects.create(
            business=business,
            name="Casa Central",
            address=business_data['address'],
            phone=business_data['phone']
        )
        
        return User.objects.create_user(
            role='admin',
            business=business,
            password=password,
            can_purchase=True,
            can_sale=True,
            can_adjust=True,
            can_transfer=True,
            **validated_data
        )

class UserCreateByAdminSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source='branch',
        write_only=True,
        required=False,
        allow_null=True
    )
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'username',
            'role', 'business', 'branch', 'branch_id',
            'password', 'can_purchase', 'can_sale',
            'can_adjust', 'can_transfer'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
            'username': {'required': True},
            'role': {'required': True}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request.user, 'business') and request.user.business:
            self.fields['branch_id'].queryset = Branch.objects.filter(business=request.user.business)
        elif request and not (hasattr(request.user, 'business') and request.user.business):
            self.fields['branch_id'].queryset = Branch.objects.none()

    def validate_name(self, value):
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("El nombre no debe contener números.")
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra minúscula.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un símbolo (ej: !@#$%&*?).")
        return value

    def validate(self, data):
        if not self.context.get('request') or not hasattr(self.context['request'], 'user'):
            raise serializers.ValidationError("Contexto de request inválido.")

        request_user = self.context['request'].user

        if not request_user.is_authenticated or getattr(request_user, 'role', None) != 'admin':
            raise serializers.ValidationError("Solo los administradores autenticados pueden crear usuarios.")

        if not getattr(request_user, 'business', None):
            raise serializers.ValidationError("El administrador debe estar asociado a una empresa para crear usuarios.")

        role = data.get('role')
        branch_instance = data.get('branch')

        if role == 'user' and not branch_instance:
            raise serializers.ValidationError({"branch_id": "Los usuarios con rol 'user' deben estar asignados a una sucursal."})

        if role == 'admin' and branch_instance:
            raise serializers.ValidationError({"branch_id": "Los administradores no deben estar asignados a una sucursal específica de esta manera."})

        if branch_instance and branch_instance.business != request_user.business:
            raise serializers.ValidationError({"branch_id": "La sucursal seleccionada no pertenece a tu empresa."})
        return data

    def create(self, validated_data):
        request_user = self.context['request'].user
        
        user_business = request_user.business
        
        branch_instance = validated_data.get('branch')
        password = validated_data.pop('password')
        
        new_user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            username=validated_data.get('username'),
            role=validated_data['role'],
            business=user_business,
            branch=branch_instance,
            can_purchase=validated_data.get('can_purchase', False),
            can_sale=validated_data.get('can_sale', False),
            can_adjust=validated_data.get('can_adjust', False),
            can_transfer=validated_data.get('can_transfer', False),
        )
        new_user.set_password(password)
        new_user.save()
        return new_user

class UserSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'username',
            'role', 'business', 'branch',
            'can_purchase', 'can_sale', 'can_adjust', 'can_transfer'
        ]