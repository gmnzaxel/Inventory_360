from rest_framework import serializers
from .models import User
from control.models import Business

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'username', 'password', 'password2', 'role']
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
        pwd = validated_data.pop('password')


        if validated_data.get('role') == 'admin' and not validated_data.get('business'):
            bus = Business.objects.create(name=f"{validated_data['name']}-Business")
            validated_data['business'] = bus

        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user
