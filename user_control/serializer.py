from rest_framework import serializers
from .models import User
from control.models import Business
from control.serializer import BusinessSerializer
import uuid

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    business = BusinessSerializer(required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'username', 'password', 'password2', 'business']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        business_data = validated_data.pop('business')
        # Crea la empresa nueva para el admin
        new_business = Business.objects.create(**business_data)
        validated_data['role'] = 'admin'

        user = User.objects.create_user(business=new_business, **validated_data)
        user.set_password(password)
        user.save()
        return user


class UserCreateByAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'name', 'role', 'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')

        # Generar username automáticamente si no se pasa
        if not validated_data.get('username'):
            base_username = validated_data['email'].split('@')[0]
            validated_data['username'] = f"{base_username}_{uuid.uuid4().hex[:6]}"

        # Asociación automática con la empresa del admin
        validated_data['business'] = self.context['request'].user.business

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

