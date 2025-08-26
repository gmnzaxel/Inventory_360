from rest_framework import serializers
from .models import User
from control.models import Business, Branch
import uuid
from control.serializer import BusinessSerializer, BranchSerializer

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'address', 'phone']

class AdminRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    business = BusinessSerializer(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'username', 'password', 'password2', 'business']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
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
        
        # Al crear el admin, se le otorgan todos los permisos por defecto
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
    branch_id = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), source='branch', write_only=True, required=False, allow_null=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'business', 'branch', 'branch_id', 'password', 'can_purchase', 'can_sale', 'can_adjust', 'can_transfer']

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated or user.role != 'admin':
            raise serializers.ValidationError("Solo los administradores pueden crear usuarios.")

        role = data.get('role')
        branch = data.get('branch')

        if role == 'user' and not branch:
            raise serializers.ValidationError("Los usuarios deben estar asignados a una sucursal.")

        if role == 'admin' and branch:
            raise serializers.ValidationError("Los administradores no deben estar asignados a una sucursal.")

        if branch and branch.business != user.business:
            raise serializers.ValidationError("La sucursal no pertenece a tu empresa.")

        return data

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            role=validated_data['role'],
            business=self.context['request'].user.business,
            branch=validated_data.get('branch'),
            can_purchase=validated_data.get('can_purchase', False),
            can_sale=validated_data.get('can_sale', False),
            can_adjust=validated_data.get('can_adjust', False),
            can_transfer=validated_data.get('can_transfer', False),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'business', 'branch', 'can_purchase', 'can_sale', 'can_adjust', 'can_transfer']