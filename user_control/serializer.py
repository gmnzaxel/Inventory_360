from rest_framework import serializers
from .models import User
from control.models import Business
from control.serializer import BranchSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    business = BranchSerializer(required=False)

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
        business_data = validated_data.pop('business', None)

        # Crear empresa automáticamente si se proporciona (para admin)
        if business_data:
            business = Business.objects.create(**business_data)
        else:
            business = Business.objects.create(name=f"{validated_data['name']}-Business")

        # Asignar rol 'admin' siempre
        user = User(
            role='admin',
            business=business,
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user


    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        business_data = validated_data.pop('business', None)

        # Crear empresa si el usuario es admin
        if validated_data.get('role') == 'admin' and business_data:
            business = Business.objects.create(**business_data)
            validated_data['business'] = business

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserCreateByAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'role', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data['business'] = self.context['request'].user.business
        user = User(**validated_data)
        user.set_password(validated_data.pop('password'))
        user.save()
        return user
